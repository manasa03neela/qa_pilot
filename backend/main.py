import asyncio
import sys

# Fix for Playwright on Windows Python 3.9
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from agent.llm import chat_with_llm
from agent.browser import BrowserAgent
import json
import re
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "QA Pilot backend is running 🚀"}


def parse_action(text: str):
    pattern = r'\[ACTION:\s*(\w+)\s*\|([^\]]*)\]'
    matches = re.findall(pattern, text)
    actions = []
    for match in matches:
        action_type = match[0].strip()
        params_raw = match[1].strip()
        params = {}
        for param in params_raw.split("|"):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key.strip()] = value.strip()
        actions.append({"type": action_type, "params": params})
    return actions


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    conversation_history = []
    browser = BrowserAgent()
    screenshot_b64 = None

    await websocket.send_text(json.dumps({
        "sender": "bot",
        "message": "👋 Hi! I'm QA Pilot — your AI testing agent.\n\nPlease share the URL of the web application you want to test!"
    }))

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_message = payload.get("message", "")

            conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Detect URL
            url_match = re.search(r'https?://[^\s]+', user_message)
            if url_match:
                url = url_match.group()
                await websocket.send_text(json.dumps({
                    "sender": "bot",
                    "message": f"🌐 Opening browser and navigating to {url}..."
                }))

                try:
                    if not browser.browser:
                        await browser.start()
                    screenshot_b64 = await browser.navigate(url)
                    await websocket.send_text(json.dumps({
                        "sender": "bot",
                        "message": "📸 Page loaded! Now analyzing with AI..."
                    }))
                except Exception as e:
                    err = traceback.format_exc()
                    print("BROWSER ERROR:\n", err)
                    await websocket.send_text(json.dumps({
                        "sender": "bot",
                        "message": f"⚠️ Browser error: {str(e)}"
                    }))

            # Get LLM response
            try:
                bot_reply = await chat_with_llm(conversation_history, screenshot_b64)
                screenshot_b64 = None
            except Exception as e:
                err = traceback.format_exc()
                print("LLM ERROR:\n", err)
                await websocket.send_text(json.dumps({
                    "sender": "bot",
                    "message": f"⚠️ AI error: {str(e)}"
                }))
                continue

            # Parse and execute actions
            actions = parse_action(bot_reply)
            for action in actions:
                try:
                    if action["type"] == "navigate":
                        url = action["params"].get("url", "")
                        screenshot_b64 = await browser.navigate(url)
                        await websocket.send_text(json.dumps({
                            "sender": "bot",
                            "message": f"🌐 Navigated to {url}"
                        }))
                    elif action["type"] == "click":
                        selector = action["params"].get("selector", "")
                        screenshot_b64 = await browser.click(selector)
                        await websocket.send_text(json.dumps({
                            "sender": "bot",
                            "message": f"🖱️ Clicked on `{selector}`"
                        }))
                    elif action["type"] == "type":
                        selector = action["params"].get("selector", "")
                        text = action["params"].get("text", "")
                        screenshot_b64 = await browser.type_text(selector, text)
                        await websocket.send_text(json.dumps({
                            "sender": "bot",
                            "message": f"⌨️ Typed into `{selector}`"
                        }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "sender": "bot",
                        "message": f"⚠️ Action failed: {str(e)}"
                    }))

            conversation_history.append({
                "role": "assistant",
                "content": bot_reply
            })

            clean_reply = re.sub(r'\[ACTION:[^\]]*\]', '', bot_reply).strip()
            await websocket.send_text(json.dumps({
                "sender": "bot",
                "message": clean_reply
            }))

    except WebSocketDisconnect:
        print("Client disconnected")
        await browser.close()
    except Exception as e:
        err = traceback.format_exc()
        print("WEBSOCKET FATAL ERROR:\n", err)
        await browser.close()
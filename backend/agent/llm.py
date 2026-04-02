import ollama
import asyncio

SYSTEM_PROMPT = """
You are QA Pilot — an expert AI testing agent that tests web applications.

You have the ability to see screenshots of the web application and perform actions.

Your behavior:
1. When given a URL, navigate to it and analyze what you see from the screenshot.
2. Plan test cases based on visible UI elements.
3. Perform actions like clicking buttons, filling forms, navigating pages.
4. If you need data from the user (credentials, file paths, form values) — ask clearly.
5. Log every test case with: Test ID, Description, Steps, Expected Result, Actual Result, Status (Pass/Fail).
6. Narrate every action you take in simple, clear language.
7. When done, summarize all results.

When you want to perform a browser action, respond with a special command block like this:

[ACTION: navigate | url=https://example.com]
[ACTION: click | selector=#login-button]
[ACTION: type | selector=#email | text=test@example.com]
[ACTION: screenshot]

Always explain what you are doing before the action command.
Always be conversational and professional.
"""

def _sync_chat(messages, screenshot_b64=None):
    """Synchronous ollama call — runs in thread"""
    if screenshot_b64:
        # For vision: attach image to last user message
        last = messages[-1]
        response = ollama.chat(
            model="gemma3:4b",
            messages=messages[:-1] + [{
                "role": "user",
                "content": last["content"],
                "images": [screenshot_b64]
            }]
        )
    else:
        response = ollama.chat(
            model="gemma3:4b",
            messages=messages
        )
    return response['message']['content']

async def chat_with_llm(conversation_history: list, screenshot_b64: str = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _sync_chat, messages, screenshot_b64)
    return response
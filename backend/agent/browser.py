import base64
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

class BrowserAgent:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="browser-agent")

    async def start(self):
        await self._run(self._start_sync)

    def _start_sync(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False  # Set True to run in background
        )
        self.page = self.browser.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 800})

    async def navigate(self, url: str) -> str:
        return await self._run(self._navigate_sync, url)

    def _navigate_sync(self, url: str) -> str:
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return self._screenshot_sync()

    async def screenshot(self) -> str:
        return await self._run(self._screenshot_sync)

    def _screenshot_sync(self) -> str:
        screenshot_bytes = self.page.screenshot(full_page=False)
        return base64.b64encode(screenshot_bytes).decode("utf-8")

    async def click(self, selector: str) -> str:
        return await self._run(self._click_sync, selector)

    def _click_sync(self, selector: str) -> str:
        self.page.click(selector, timeout=10000)
        self.page.wait_for_timeout(1000)
        return self._screenshot_sync()

    async def type_text(self, selector: str, text: str) -> str:
        return await self._run(self._type_text_sync, selector, text)

    def _type_text_sync(self, selector: str, text: str) -> str:
        self.page.fill(selector, text)
        self.page.wait_for_timeout(500)
        return self._screenshot_sync()

    async def get_page_content(self) -> str:
        return await self._run(self.page.inner_text, "body")

    async def get_page_url(self) -> str:
        return await self._run(lambda: self.page.url)

    async def close(self):
        try:
            await self._run(self._close_sync)
        finally:
            self._executor.shutdown(wait=False)

    def _close_sync(self):
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        self.page = None

    async def _run(self, fn, *args):
        import asyncio

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: fn(*args))

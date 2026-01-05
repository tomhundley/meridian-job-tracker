"""Playwright browser management with persistent sessions."""

import asyncio
from pathlib import Path
from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from src.config import settings


class BrowserManager:
    """
    Manages Playwright browser instances with persistent session storage.

    Features:
    - Persistent login sessions (saves cookies/storage)
    - Human-like interaction delays
    - Screenshot capture for debugging
    - Headful mode for human-in-the-loop
    """

    def __init__(
        self,
        user_data_dir: Path | None = None,
        headless: bool = False,
        slow_mo: int = 100,
    ):
        self.user_data_dir = user_data_dir or Path.home() / ".meridian-job-tracker" / "browser"
        self.headless = headless
        self.slow_mo = slow_mo

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

        # Ensure user data directory exists
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def storage_state_path(self) -> Path:
        """Path to saved browser storage state."""
        return self.user_data_dir / "storage_state.json"

    async def start(self) -> None:
        """Start the browser."""
        if self._playwright is not None:
            return

        self._playwright = await async_playwright().start()

        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        # Create context with persistent storage if available
        storage_state = None
        if self.storage_state_path.exists():
            storage_state = str(self.storage_state_path)

        self._context = await self._browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

    async def stop(self) -> None:
        """Stop the browser and save session."""
        if self._context:
            await self.save_session()
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def save_session(self) -> None:
        """Save browser session state for reuse."""
        if self._context:
            await self._context.storage_state(path=str(self.storage_state_path))

    async def get_context(self) -> BrowserContext:
        """Get the browser context, starting browser if needed."""
        if self._context is None:
            await self.start()
        return self._context  # type: ignore

    async def new_page(self) -> Page:
        """Create a new page in the browser context."""
        context = await self.get_context()
        return await context.new_page()

    async def take_screenshot(self, page: Page, name: str) -> Path:
        """Take a screenshot and save it."""
        screenshots_dir = self.user_data_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = screenshots_dir / f"{name}_{timestamp}.png"

        await page.screenshot(path=str(path), full_page=False)
        return path

    async def __aenter__(self) -> "BrowserManager":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()


class LinkedInAuth:
    """Handle LinkedIn authentication."""

    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.login_url = "https://www.linkedin.com/login"
        self.feed_url = "https://www.linkedin.com/feed/"

    async def is_logged_in(self, page: Page) -> bool:
        """Check if already logged in to LinkedIn."""
        # Navigate to feed and check if redirected to login
        await page.goto(self.feed_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        current_url = page.url
        return "login" not in current_url and "checkpoint" not in current_url

    async def login(
        self,
        email: str | None = None,
        password: str | None = None,
        page: Page | None = None,
    ) -> bool:
        """
        Log in to LinkedIn.

        If credentials are not provided, uses settings.
        Returns True if login successful.
        """
        email = email or settings.linkedin_email
        password = password or settings.linkedin_password

        if not email or not password:
            raise ValueError("LinkedIn credentials not configured")

        if page is None:
            page = await self.browser.new_page()

        # Check if already logged in
        if await self.is_logged_in(page):
            return True

        # Navigate to login page
        await page.goto(self.login_url, wait_until="domcontentloaded")
        await asyncio.sleep(1)

        # Fill credentials
        await page.fill('input[name="session_key"]', email)
        await page.fill('input[name="session_password"]', password)

        # Click sign in
        await page.click('button[type="submit"]')

        # Wait for navigation
        await asyncio.sleep(3)

        # Check for security checkpoint or successful login
        current_url = page.url

        if "checkpoint" in current_url:
            # Security verification needed - requires human intervention
            print("Security checkpoint detected. Please complete verification in the browser.")
            # Wait for human to complete verification (up to 2 minutes)
            for _ in range(24):  # 24 * 5 seconds = 2 minutes
                await asyncio.sleep(5)
                if "checkpoint" not in page.url:
                    break

        # Save session after successful login
        await self.browser.save_session()

        return await self.is_logged_in(page)


# Global browser manager instance
_browser_manager: BrowserManager | None = None


async def get_browser_manager() -> BrowserManager:
    """Get the global browser manager instance."""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
    return _browser_manager


async def cleanup_browser() -> None:
    """Cleanup the global browser manager."""
    global _browser_manager
    if _browser_manager:
        await _browser_manager.stop()
        _browser_manager = None

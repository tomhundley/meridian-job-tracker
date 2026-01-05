"""LinkedIn job application automation with human-in-the-loop."""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from src.services import resume_service

from .browser import BrowserManager, LinkedInAuth, get_browser_manager


class ApplicationStep(str, Enum):
    """Steps in the application process."""

    NAVIGATING = "navigating"
    ANALYZING_PAGE = "analyzing_page"
    CLICKING_APPLY = "clicking_apply"
    FILLING_FORM = "filling_form"
    UPLOADING_RESUME = "uploading_resume"
    ADDING_COVER_LETTER = "adding_cover_letter"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    SUBMITTING = "submitting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FormField:
    """Represents a form field to fill."""

    name: str
    value: str
    selector: str
    field_type: str = "text"  # text, select, checkbox, file


@dataclass
class ApplicationState:
    """Current state of an application attempt."""

    job_url: str
    step: ApplicationStep = ApplicationStep.NAVIGATING
    job_title: str | None = None
    company: str | None = None
    form_fields: list[FormField] = field(default_factory=list)
    filled_fields: dict[str, str] = field(default_factory=dict)
    error_message: str | None = None
    screenshot_path: str | None = None
    requires_confirmation: bool = False
    is_easy_apply: bool = False


@dataclass
class ApplicationResult:
    """Result of an application attempt."""

    success: bool
    job_url: str
    job_title: str | None = None
    company: str | None = None
    error_message: str | None = None
    screenshot_path: str | None = None
    form_data: dict[str, Any] = field(default_factory=dict)
    confirmation_text: str | None = None


class LinkedInApply:
    """
    Handles LinkedIn Easy Apply and full application flows.

    Features:
    - Detects Easy Apply vs external application
    - Auto-fills form fields from resume data
    - Pauses for human confirmation before submit
    - Captures screenshots at each step
    """

    def __init__(self, browser_manager: BrowserManager | None = None):
        self._browser_manager = browser_manager
        self._auth: LinkedInAuth | None = None

    async def get_browser(self) -> BrowserManager:
        """Get the browser manager."""
        if self._browser_manager is None:
            self._browser_manager = await get_browser_manager()
        return self._browser_manager

    async def get_auth(self) -> LinkedInAuth:
        """Get the LinkedIn auth handler."""
        if self._auth is None:
            browser = await self.get_browser()
            self._auth = LinkedInAuth(browser)
        return self._auth

    async def apply(
        self,
        job_url: str,
        resume_path: Path | None = None,
        cover_letter: str | None = None,
        auto_submit: bool = False,
    ) -> ApplicationResult:
        """
        Apply to a job on LinkedIn.

        Args:
            job_url: URL of the LinkedIn job posting
            resume_path: Path to resume PDF (optional)
            cover_letter: Cover letter text (optional)
            auto_submit: If True, submit without human confirmation (not recommended)

        Returns:
            ApplicationResult with success status and details
        """
        browser = await self.get_browser()
        state = ApplicationState(job_url=job_url)

        try:
            page = await browser.new_page()

            # Ensure logged in
            auth = await self.get_auth()
            if not await auth.is_logged_in(page):
                if not await auth.login(page=page):
                    state.step = ApplicationStep.FAILED
                    state.error_message = "Failed to log in to LinkedIn"
                    screenshot = await browser.take_screenshot(page, "login_failed")
                    return ApplicationResult(
                        success=False,
                        job_url=job_url,
                        error_message=state.error_message,
                        screenshot_path=str(screenshot),
                    )

            # Navigate to job posting
            state.step = ApplicationStep.NAVIGATING
            await page.goto(job_url, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # Analyze the page
            state.step = ApplicationStep.ANALYZING_PAGE
            job_info = await self._extract_job_info(page)
            state.job_title = job_info.get("title")
            state.company = job_info.get("company")

            # Check for Easy Apply button
            easy_apply_button = page.locator('button:has-text("Easy Apply")')
            if await easy_apply_button.count() > 0:
                state.is_easy_apply = True
                return await self._handle_easy_apply(
                    page=page,
                    state=state,
                    browser=browser,
                    resume_path=resume_path,
                    cover_letter=cover_letter,
                    auto_submit=auto_submit,
                )
            else:
                # External application - just provide info
                screenshot = await browser.take_screenshot(page, "external_application")
                return ApplicationResult(
                    success=False,
                    job_url=job_url,
                    job_title=state.job_title,
                    company=state.company,
                    error_message="External application required - Easy Apply not available",
                    screenshot_path=str(screenshot),
                )

        except PlaywrightTimeout as e:
            screenshot_path = None
            try:
                browser = await self.get_browser()
                page = await browser.new_page()
                screenshot = await browser.take_screenshot(page, "timeout_error")
                screenshot_path = str(screenshot)
            except Exception:
                pass

            return ApplicationResult(
                success=False,
                job_url=job_url,
                error_message=f"Timeout: {str(e)}",
                screenshot_path=screenshot_path,
            )

        except Exception as e:
            return ApplicationResult(
                success=False,
                job_url=job_url,
                error_message=str(e),
            )

    async def _extract_job_info(self, page: Page) -> dict[str, str]:
        """Extract job title and company from the page."""
        info = {}

        try:
            # Job title
            title_elem = page.locator("h1.job-details-jobs-unified-top-card__job-title")
            if await title_elem.count() > 0:
                info["title"] = await title_elem.inner_text()

            # Company name
            company_elem = page.locator(".job-details-jobs-unified-top-card__company-name")
            if await company_elem.count() > 0:
                info["company"] = await company_elem.inner_text()

        except Exception:
            pass

        return info

    async def _handle_easy_apply(
        self,
        page: Page,
        state: ApplicationState,
        browser: BrowserManager,
        resume_path: Path | None,
        cover_letter: str | None,
        auto_submit: bool,
    ) -> ApplicationResult:
        """Handle the Easy Apply flow."""
        state.step = ApplicationStep.CLICKING_APPLY

        # Click Easy Apply button
        easy_apply_button = page.locator('button:has-text("Easy Apply")')
        await easy_apply_button.click()
        await asyncio.sleep(2)

        # Process form steps
        max_steps = 10  # Safety limit
        for step_num in range(max_steps):
            state.step = ApplicationStep.FILLING_FORM

            # Fill visible form fields
            await self._fill_form_fields(page, state)

            # Check for file upload (resume)
            file_input = page.locator('input[type="file"]')
            if await file_input.count() > 0 and resume_path and resume_path.exists():
                state.step = ApplicationStep.UPLOADING_RESUME
                await file_input.set_input_files(str(resume_path))
                await asyncio.sleep(1)

            # Check for cover letter text area
            cover_letter_input = page.locator('textarea[name*="cover" i], textarea[aria-label*="cover" i]')
            if await cover_letter_input.count() > 0 and cover_letter:
                state.step = ApplicationStep.ADDING_COVER_LETTER
                await cover_letter_input.fill(cover_letter)

            # Look for Review or Submit button
            review_button = page.locator('button:has-text("Review")')
            submit_button = page.locator('button[aria-label*="Submit application" i]')
            next_button = page.locator('button:has-text("Next")')

            if await submit_button.count() > 0:
                # We're at the submit step
                state.step = ApplicationStep.AWAITING_CONFIRMATION
                state.requires_confirmation = True

                # Take screenshot for human review
                screenshot = await browser.take_screenshot(page, "pre_submit_review")
                state.screenshot_path = str(screenshot)

                if not auto_submit:
                    # Return for human confirmation
                    return ApplicationResult(
                        success=False,  # Not yet successful - awaiting confirmation
                        job_url=state.job_url,
                        job_title=state.job_title,
                        company=state.company,
                        error_message="Awaiting human confirmation to submit",
                        screenshot_path=str(screenshot),
                        form_data=state.filled_fields,
                    )

                # Auto submit if enabled
                state.step = ApplicationStep.SUBMITTING
                await submit_button.click()
                await asyncio.sleep(3)

                # Check for success
                state.step = ApplicationStep.COMPLETED
                screenshot = await browser.take_screenshot(page, "post_submit")

                return ApplicationResult(
                    success=True,
                    job_url=state.job_url,
                    job_title=state.job_title,
                    company=state.company,
                    screenshot_path=str(screenshot),
                    form_data=state.filled_fields,
                    confirmation_text="Application submitted successfully",
                )

            elif await review_button.count() > 0:
                await review_button.click()
                await asyncio.sleep(2)

            elif await next_button.count() > 0:
                await next_button.click()
                await asyncio.sleep(2)

            else:
                # No navigation button found
                break

        # If we reach here, something went wrong
        screenshot = await browser.take_screenshot(page, "form_navigation_failed")
        return ApplicationResult(
            success=False,
            job_url=state.job_url,
            job_title=state.job_title,
            company=state.company,
            error_message="Could not complete form navigation",
            screenshot_path=str(screenshot),
            form_data=state.filled_fields,
        )

    async def _fill_form_fields(self, page: Page, state: ApplicationState) -> None:
        """Fill form fields with resume data."""
        personal = resume_service.personal_info

        # Common field mappings
        field_mappings = {
            "email": personal.get("email", ""),
            "phone": personal.get("phone", ""),
            "first name": personal.get("name", "").split()[0] if personal.get("name") else "",
            "last name": personal.get("name", "").split()[-1] if personal.get("name") else "",
            "city": personal.get("location", "").split(",")[0] if personal.get("location") else "",
            "linkedin": personal.get("linkedin", ""),
            "website": personal.get("website", ""),
        }

        # Find and fill text inputs
        inputs = page.locator("input[type='text'], input[type='email'], input[type='tel']")
        count = await inputs.count()

        for i in range(count):
            input_elem = inputs.nth(i)

            try:
                # Get label or placeholder
                label = await input_elem.get_attribute("aria-label") or ""
                placeholder = await input_elem.get_attribute("placeholder") or ""
                name = await input_elem.get_attribute("name") or ""

                identifier = f"{label} {placeholder} {name}".lower()

                # Try to match with our data
                for key, value in field_mappings.items():
                    if key in identifier and value:
                        current_value = await input_elem.input_value()
                        if not current_value:  # Only fill if empty
                            await input_elem.fill(value)
                            state.filled_fields[key] = value
                            break

            except Exception:
                continue

    async def confirm_and_submit(
        self,
        page: Page,
    ) -> ApplicationResult:
        """
        Submit an application after human confirmation.

        Call this after reviewing the pre-submit screenshot.
        """
        browser = await self.get_browser()

        try:
            submit_button = page.locator('button[aria-label*="Submit application" i]')
            if await submit_button.count() > 0:
                await submit_button.click()
                await asyncio.sleep(3)

                screenshot = await browser.take_screenshot(page, "post_submit_confirmed")

                return ApplicationResult(
                    success=True,
                    job_url=page.url,
                    screenshot_path=str(screenshot),
                    confirmation_text="Application submitted after confirmation",
                )

        except Exception as e:
            screenshot = await browser.take_screenshot(page, "submit_error")
            return ApplicationResult(
                success=False,
                job_url=page.url,
                error_message=str(e),
                screenshot_path=str(screenshot),
            )

        return ApplicationResult(
            success=False,
            job_url=page.url,
            error_message="Submit button not found",
        )


# Singleton instance
linkedin_apply = LinkedInApply()

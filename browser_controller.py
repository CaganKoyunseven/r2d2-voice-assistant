"""
Browser handler — opens configured URLs on trigger event.
"""
import logging
import time
import webbrowser

import config

logger = logging.getLogger(__name__)

_URL_OPEN_DELAY = 0.5  # seconds between tabs to avoid race conditions


def open_all_urls() -> None:
    """Opens all URLs from config.URLS in the default (or configured) browser."""
    try:
        browser = webbrowser.get(config.BROWSER)
    except webbrowser.Error:
        logger.warning("Browser '%s' not found, using system default", config.BROWSER)
        browser = webbrowser.get()

    for name, url in config.URLS.items():
        try:
            browser.open(url)
            logger.info("Opened: %s → %s", name, url)
            time.sleep(_URL_OPEN_DELAY)
        except Exception:
            logger.exception("Failed to open URL: %s", url)


def handle(event: str) -> None:
    """CommandDispatcher handler interface."""
    open_all_urls()

# features/environment.py
# Use Chromium + Chromedriver if available; otherwise fall back to Selenium Manager.

import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service


def _exists(p: str | None) -> bool:
    return bool(p and os.path.exists(p))


def _which(*names: str) -> str | None:
    for n in names:
        path = shutil.which(n)
        if _exists(path):
            return path
    return None


def _find_chrome_binary() -> str | None:
    # Explicit override via env
    env_path = os.getenv("CHROME_BIN")
    if _exists(env_path):
        return env_path
    # Common binaries
    candidates = [
        _which("chromium"),
        _which("chromium-browser"),
        _which("google-chrome"),
        _which("google-chrome-stable"),
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
    ]
    for c in candidates:
        if _exists(c):
            return c
    return None


def _find_chromedriver() -> str | None:
    # Explicit override via env
    env_path = os.getenv("CHROMEDRIVER")
    if _exists(env_path):
        return env_path
    # Common locations
    candidates = [
        _which("chromedriver"),
        "/usr/bin/chromedriver",
        "/usr/lib/chromium/chromedriver",
        "/snap/bin/chromium.chromedriver",
    ]
    for c in candidates:
        if _exists(c):
            return c
    return None


def before_all(context):
    """Initialize a headless Chromium WebDriver with best-effort driver discovery."""
    headless = os.getenv("HEADLESS", "true").lower() == "true"

    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    # Container-friendly flags
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")

    # Point to Chromium binary if Chrome is not installed
    chrome_bin = _find_chrome_binary()
    if chrome_bin:
        opts.binary_location = chrome_bin

    # Prefer a locally installed chromedriver to avoid network downloads
    driver_path = _find_chromedriver()

    if driver_path:
        service = Service(executable_path=driver_path)
        context.browser = webdriver.Chrome(service=service, options=opts)
    else:
        # Fall back to Selenium Manager (requires network & compatible binary)
        context.browser = webdriver.Chrome(options=opts)


def after_all(context):
    """Tear down the WebDriver (guarded)."""
    browser = getattr(context, "browser", None)
    if browser is not None:
        browser.quit()

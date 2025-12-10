# features/environment.py
# Use Chromium + Chromedriver

import os
import shutil
import sys
from typing import Any

import requests
from requests import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
API_BASE_URL = os.getenv("API_BASE_URL", f"{BASE_URL}/api").rstrip("/")
RESET_TIMEOUT = int(os.getenv("RESET_TIMEOUT", "15"))
SEED_ITEMS = [
    {
        "name": "First Item",
        "sku": "seed-first-item",
        "quantity": 7,
        "category": "test",
        "description": "seed data",
        "price": 5.0,
        "available": True,
    }
]


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


def _api_url(path: str) -> str:
    """Build an absolute API URL from a relative path."""
    trimmed = path.strip("/")
    return f"{API_BASE_URL}/{trimmed}"


def _reset_inventory_state() -> None:
    """Ensure each scenario begins with a clean, known dataset."""
    session = requests.Session()
    try:
        resp = session.get(_api_url("inventory"), timeout=RESET_TIMEOUT)
        resp.raise_for_status()
        payload: list[Any] = resp.json() or []
    except RequestException as err:
        raise RuntimeError(f"Unable to list inventory: {err}") from err

    for item in payload:
        inv_id = item.get("id")
        if inv_id is None:
            continue
        try:
            session.delete(
                _api_url(f"inventory/{inv_id}"), timeout=RESET_TIMEOUT
            ).raise_for_status()
        except RequestException as err:
            raise RuntimeError(f"Unable to delete inventory {inv_id}: {err}") from err

    for seed in SEED_ITEMS:
        try:
            session.post(
                _api_url("inventory"),
                json=seed,
                timeout=RESET_TIMEOUT,
            ).raise_for_status()
        except RequestException as err:
            raise RuntimeError(f"Unable to seed inventory data: {err}") from err


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


def before_scenario(context, scenario):  # pylint: disable=unused-argument
    """Reset API data so every scenario starts from a known baseline."""
    try:
        _reset_inventory_state()
    except RuntimeError as err:
        print(f"[behave] Failed to reset inventory via API: {err}", file=sys.stderr)
        raise


def after_all(context):
    """Tear down the WebDriver (guarded)."""
    browser = getattr(context, "browser", None)
    if browser is not None:
        browser.quit()

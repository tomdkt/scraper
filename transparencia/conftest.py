import os, pytest
from playwright.sync_api import sync_playwright, Browser

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

@pytest.fixture(scope="session")
def browser() -> Browser:
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=HEADLESS, slow_mo=250)
        yield b
        b.close()
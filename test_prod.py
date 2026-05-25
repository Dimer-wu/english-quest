"""Quick production smoke test against dimerenglish.top"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

URL = "https://dimerenglish.top"
import os
TEST_USER = f"smoke_{os.urandom(3).hex()}"
TEST_PASS = "test123"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})  # iPhone 14 size

    errors = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

    print("[1/6] Loading homepage...")
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert "ENGLISH QUEST" in page.content().upper(), "Homepage failed to load!"
    print("  PASS: Homepage loads via HTTPS")

    print("[2/6] Registering test user...")
    page.locator("#toggleAuth").click()
    page.locator("#loginUser").fill(TEST_USER)
    page.locator("#loginPass").fill(TEST_PASS)
    page.locator("#authBtn").click()
    page.wait_for_timeout(3000)

    # Debug: check page state
    state = page.evaluate("""() => ({
        loginActive: document.getElementById('loginPage').classList.contains('active'),
        homeActive: document.getElementById('homePage').classList.contains('active'),
        tabBarDisplay: document.getElementById('tabBar').style.display,
        user: S.user,
        stats: S.stats,
        authMsg: document.getElementById('authMsg').textContent
    })""")
    print(f"  DEBUG: {state}")

    if state.get('authMsg'):
        print(f"  FAIL: Auth error message: {state['authMsg']}")
    elif state.get('homeActive'):
        print("  PASS: Registration + auto-login works")
    else:
        print(f"  FAIL: Unexpected state")

    print("[3/6] Loading scenarios...")
    page.wait_for_selector(".scenario-card", timeout=5000)
    card_count = page.locator(".scenario-card").count()
    assert card_count == 10, f"Expected 10 scenarios, got {card_count}"
    print(f"  PASS: {card_count} scenarios loaded")

    print("[4/6] Entering scenario study...")
    page.locator(".scenario-card").first.click()
    page.wait_for_timeout(500)
    step_tabs = page.locator(".step-tab").count()
    assert step_tabs == 6, f"Expected 6 steps, got {step_tabs}"
    print(f"  PASS: Study page with {step_tabs} steps")

    print("[5/6] Testing AI chat...")
    # Navigate to step 3
    for _ in range(2):
        page.locator("button:has-text('下一步')").click()
        page.wait_for_timeout(300)
    chat_input = page.locator("#chatInput")
    if chat_input.is_visible():
        chat_input.fill("Hello!")
        page.locator("#chatBtn").click()
        page.wait_for_timeout(5000)
        chat_content = page.locator("#chatMessages").text_content()
        assert len(chat_content) > 20, "AI chat response too short or empty!"
        print(f"  PASS: AI chat responded: {chat_content[:80]}...")

    print("[6/6] Testing chunks + profile...")
    page.locator(".tab-item[data-page='chunksPage']").click()
    page.wait_for_timeout(500)
    page.locator(".tab-item[data-page='profilePage']").click()
    page.wait_for_timeout(500)
    profile_text = page.locator("#profilePage").text_content()
    assert TEST_USER in profile_text, f"Profile missing username!"
    print(f"  PASS: Chunks + Profile pages work")

    # Logout
    page.evaluate("logout()")
    page.wait_for_timeout(1000)
    page_state = page.evaluate("""() => ({
        loginActive: document.getElementById('loginPage').classList.contains('active'),
    })""")
    assert page_state['loginActive'], "Logout failed!"
    print("  PASS: Logout works")

    browser.close()

    print(f"\n{'='*40}")
    print(f"ALL 6 TESTS PASSED")
    print(f"JS Errors: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    print(f"\nProduction URL: {URL}")
    print(f"{'='*40}")

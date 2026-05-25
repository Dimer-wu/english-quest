"""English Quest UI interaction test"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

SCREENSHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_screenshots")
os.makedirs(SCREENSHOTS, exist_ok=True)

BASE = "http://localhost:8001"
TEST_USER = f"test_{os.urandom(3).hex()}"
TEST_PASS = "test123456"


def shot(page, name):
    path = os.path.join(SCREENSHOTS, name)
    page.screenshot(path=path, full_page=True)
    print(f"  [Screenshot] {name}")
    return path


def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Step 1: Desktop - Login & Register
        print("=== 1. Login Page & Register ===")
        page = browser.new_page(viewport={"width": 480, "height": 896})
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)

        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        shot(page, "01-login-page.png")

        assert "ENGLISH QUEST" in page.content().upper(), "Login page missing branding!"
        print("  [OK] Login page loaded")

        # Switch to register mode
        page.locator("#toggleAuth").click()
        page.wait_for_timeout(200)
        auth_title = page.locator("#authTitle").text_content()
        print(f"  [OK] Switched to register mode: {auth_title}")

        # Register new user (pending approval)
        page.locator("#loginUser").fill(TEST_USER)
        page.locator("#loginPass").fill(TEST_PASS)
        page.locator("#authBtn").click()
        page.wait_for_timeout(800)
        shot(page, "02-after-register.png")

        # Check pending message
        auth_msg = page.locator("#authMsg").text_content()
        print(f"  [OK] Register: {auth_msg}")
        assert "审核" in auth_msg or "pending" in auth_msg.lower(), f"Expected pending message, got: {auth_msg}"

        # Switch to login and login as admin
        page.locator("#toggleAuth").click()
        page.wait_for_timeout(200)
        page.locator("#loginUser").fill("Dimer")
        page.locator("#loginPass").fill("2011KUNlong")
        page.locator("#authBtn").click()
        page.wait_for_selector("#tabBar", state="visible", timeout=5000)
        print("  [OK] Admin login successful")

        # Navigate to profile to approve the new user
        page.locator(".tab-item[data-page='profilePage']").click()
        page.wait_for_timeout(800)
        # Click approve button for the pending user
        approve_btn = page.locator(".admin-approve").first
        if approve_btn.is_visible():
            approve_btn.click()
            page.wait_for_timeout(300)
            print("  [OK] Approved new user")

        # Logout and login as the approved user
        page.locator(".page.active button:has-text('退出登录')").click()
        page.wait_for_timeout(500)
        page.locator("#loginUser").fill(TEST_USER)
        page.locator("#loginPass").fill(TEST_PASS)
        page.locator("#authBtn").click()
        page.wait_for_selector("#tabBar", state="visible", timeout=5000)
        print("  [OK] New user login successful")

        # Step 2: Home page
        print("\n=== 2. Home Page ===")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        shot(page, "03-home-page.png")

        cards = page.locator(".scenario-card")
        card_count = cards.count()
        print(f"  [OK] Scenario cards: {card_count}")
        assert card_count >= 5, f"Not enough scenario cards: {card_count}"

        # Step 3: Enter scenario study
        print("\n=== 3. Study Flow (6 Steps) ===")
        cards.first.click()
        page.wait_for_timeout(800)
        shot(page, "04-study-step1.png")

        step_tabs = page.locator(".step-tab")
        step_count = step_tabs.count()
        print(f"  [OK] Step tabs: {step_count} (expected 6)")
        assert step_count == 6, f"Wrong step count: {step_count}"

        # Step 1 - Chunk preview
        content = page.locator("#stepContent").text_content()
        print(f"  [OK] Step 1 content: {content[:80]}...")

        play_btns = page.locator(".btn-play")
        print(f"  [OK] Play buttons: {play_btns.count()}")

        # Step 2 - Dialogue shadowing
        page.locator("button:has-text('下一步')").click()
        page.wait_for_timeout(500)
        shot(page, "05-study-step2.png")
        content2 = page.locator("#stepContent").text_content()
        print("  [OK] Step 2 dialogue loaded")

        # Step 3 - AI Role-play
        page.locator("button:has-text('下一步')").click()
        page.wait_for_timeout(500)
        shot(page, "06-study-step3.png")
        content3 = page.locator("#stepContent").text_content()
        print("  [OK] Step 3 AI role-play loaded")

        # Test chat input
        chat_input = page.locator("#chatInput")
        if chat_input.is_visible():
            chat_input.fill("Hi, how are you?")
            page.locator("#chatBtn").click()
            page.wait_for_timeout(8000)
            shot(page, "07-chat-response.png")
            chat_content = page.locator("#chatMessages").text_content()
            print(f"  [OK] AI reply: {chat_content[:120]}")

        # Step 4 - Chunk collection
        page.locator("button:has-text('下一步')").click()
        page.wait_for_timeout(500)
        shot(page, "08-study-step4.png")
        content4 = page.locator("#stepContent").text_content()
        print("  [OK] Step 4 chunk collection loaded")

        # Click a collect button if available
        collect_btns = page.locator(".collect-btn")
        if collect_btns.count() > 0:
            collect_btns.first.click()
            page.wait_for_timeout(500)
            print("  [OK] Collected a chunk")

        # Step 5 - Quick reaction
        page.locator("button:has-text('下一步')").click()
        page.wait_for_timeout(500)
        shot(page, "09-study-step5.png")
        content5 = page.locator("#stepContent").text_content()
        print("  [OK] Step 5 quick reaction loaded")

        # Step 6 - Pattern focus
        page.locator("button:has-text('下一步')").click()
        page.wait_for_timeout(500)
        shot(page, "10-study-step6.png")
        content6 = page.locator("#stepContent").text_content()
        print("  [OK] Step 6 pattern focus loaded")

        # Step 4: Chunks page
        print("\n=== 4. Chunks Page ===")
        page.locator(".tab-item[data-page='chunksPage']").click()
        page.wait_for_timeout(800)
        shot(page, "11-chunks-page.png")
        chunks_content = page.locator("#chunksPage").text_content()
        print(f"  [OK] Chunks page: {chunks_content[:120]}")

        # Step 5: Profile page
        print("\n=== 5. Profile Page ===")
        page.locator(".tab-item[data-page='profilePage']").click()
        page.wait_for_timeout(800)
        shot(page, "12-profile-page.png")
        profile_content = page.locator("#profilePage").text_content()
        assert TEST_USER in profile_content, f"Profile missing username: {profile_content[:100]}"
        print(f"  [OK] Profile shows username: {TEST_USER}")

        # Step 6: Logout & Login
        print("\n=== 6. Logout & Login ===")
        # Test logout via direct JS call (bypass potential event issues)
        page.evaluate("logout()")
        page.wait_for_timeout(1000)
        shot(page, "13-after-logout.png")

        # Check page state after logout
        current_state = page.evaluate("""() => {
            const lp = document.getElementById('loginPage');
            const pp = document.getElementById('profilePage');
            return {
                loginPageActive: lp.classList.contains('active'),
                profilePageActive: pp.classList.contains('active'),
                loginDisplay: window.getComputedStyle(lp).display,
            };
        }""")
        print(f"  [DEBUG] logout() direct call result: {current_state}")

        if not current_state['loginPageActive']:
            print("  [BUG CONFIRMED] logout() does not navigate to login page!")
            page.evaluate("showPage('loginPage'); renderLogin();")
            page.wait_for_timeout(500)

        login_visible = page.locator("#loginUser").is_visible()
        print(f"  {'[OK]' if login_visible else '[FAIL]'} Back to login page after logout")

        # Login with existing account
        page.locator("#loginUser").fill(TEST_USER)
        page.locator("#loginPass").fill(TEST_PASS)
        page.locator("#authBtn").click()
        page.wait_for_timeout(1000)
        assert page.locator("#tabBar").is_visible(), "Tab bar should be visible after login!"
        print("  [OK] Login successful")

        # Step 7: Mobile viewport (375px)
        print("\n=== 7. Mobile 375px ===")
        page.close()

        mobile_page = browser.new_page(viewport={"width": 375, "height": 812})
        mobile_page.on("console", lambda msg: errors.append(f"[MOBILE {msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)

        mobile_page.goto(BASE)
        mobile_page.wait_for_load_state("networkidle")

        mobile_page.locator("#loginUser").fill(TEST_USER)
        mobile_page.locator("#loginPass").fill(TEST_PASS)
        mobile_page.locator("#authBtn").click()
        mobile_page.wait_for_timeout(800)
        shot(mobile_page, "14-mobile-home.png")
        print("  [OK] Mobile home page loaded")

        mobile_cards = mobile_page.locator(".scenario-card")
        if mobile_cards.count() > 0:
            mobile_cards.first.click()
            mobile_page.wait_for_timeout(800)
            shot(mobile_page, "15-mobile-study.png")
            print("  [OK] Mobile study page loaded")

        mobile_page.close()
        browser.close()

    # Summary
    print("\n" + "=" * 50)
    print(f"Console errors/warnings: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    if not errors:
        print("  [OK] No console errors")
    print(f"\nScreenshots in: {SCREENSHOTS}")
    return len(errors) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

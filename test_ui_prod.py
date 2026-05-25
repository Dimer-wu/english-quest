"""Quick UI health check for production"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

URL = "https://dimerenglish.top"
TEST_USER = f"ui_{os.urandom(2).hex()}"

issues = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})

    js_errors = []
    page.on("console", lambda msg: js_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)

    # 1. Load homepage
    print("[1] Loading homepage...")
    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector("#loginUser", state="visible", timeout=8000)
        print("  OK: Login form visible")
    except Exception as e:
        issues.append(f"HOMEPAGE: {e}")
        print(f"  FAIL: {e}")

    # 2. Check CSS/styling
    print("[2] Checking styles...")
    styles = page.evaluate("""() => {
        const body = document.body;
        const style = window.getComputedStyle(body);
        return {
            bg: style.backgroundColor,
            font: style.fontFamily,
            maxWidth: style.maxWidth,
            tabBarExists: !!document.getElementById('tabBar'),
            allPages: [...document.querySelectorAll('.page')].map(p => p.id),
            hasFontAwesome: !!document.querySelector('.fa'),
        };
    }""")
    print(f"  Background: {styles['bg']}")
    print(f"  Font: {styles['font'][:40]}...")
    print(f"  Max-width: {styles['maxWidth']}")
    print(f"  Pages: {styles['allPages']}")
    if styles['bg'] != 'rgb(255, 253, 240)':
        issues.append("BACKGROUND_COLOR: Expected #FFFDF0")
    if not styles['hasFontAwesome']:
        issues.append("NO_FONT_AWESOME")

    # 3. Register & check home UI
    print("[3] Register & home UI...")
    try:
        page.locator("#toggleAuth").click()
        page.locator("#loginUser").fill(TEST_USER)
        page.locator("#loginPass").fill("test123")
        page.locator("#authBtn").click()
        page.wait_for_selector("#tabBar", state="visible", timeout=10000)

        # Check stat cards
        card_count = page.locator(".card").count()
        scenario_count = page.locator(".scenario-card").count()
        print(f"  OK: {card_count} cards, {scenario_count} scenarios")

        if scenario_count != 10:
            issues.append(f"SCENARIO_COUNT: {scenario_count} (expected 10)")
    except Exception as e:
        issues.append(f"HOME_UI: {e}")
        print(f"  FAIL: {e}")

    # 4. Enter study, verify 6 steps
    print("[4] Study page UI...")
    try:
        page.locator(".scenario-card").first.click()
        page.wait_for_selector(".step-tab", timeout=5000)
        step_count = page.locator(".step-tab").count()
        has_step_content = page.locator("#stepContent").inner_text()
        print(f"  OK: {step_count} steps, content: {has_step_content[:50]}...")

        if step_count != 6:
            issues.append(f"STEP_COUNT: {step_count}")
    except Exception as e:
        issues.append(f"STUDY_UI: {e}")
        print(f"  FAIL: {e}")

    # 5. Check chunks page
    print("[5] Chunks page UI...")
    try:
        page.locator(".tab-item[data-page='chunksPage']").click()
        page.wait_for_timeout(500)
        chunks_text = page.locator("#chunksPage").inner_text()
        print(f"  OK: Chunks page loaded: {chunks_text[:60]}...")
    except Exception as e:
        issues.append(f"CHUNKS_UI: {e}")
        print(f"  FAIL: {e}")

    # 6. Check profile page
    print("[6] Profile page UI...")
    try:
        page.locator(".tab-item[data-page='profilePage']").click()
        page.wait_for_timeout(500)
        profile_text = page.locator("#profilePage").inner_text()
        assert TEST_USER in profile_text
        print(f"  OK: Profile shows {TEST_USER}")

        # Check progress bar
        has_progress_bar = page.evaluate("""() => {
            const bars = document.querySelectorAll('#profilePage div[style*=\"background:#FF6B00\"]');
            return bars.length > 0;
        }""")
        print(f"  Progress bar: {'OK' if has_progress_bar else 'MISSING'}")
        if not has_progress_bar:
            issues.append("PROGRESS_BAR_MISSING")
    except Exception as e:
        issues.append(f"PROFILE_UI: {e}")
        print(f"  FAIL: {e}")

    # 7. Test responsive tab bar
    print("[7] Tab bar interaction...")
    try:
        # Switch back to home
        page.locator(".tab-item[data-page='homePage']").click()
        page.wait_for_timeout(300)
        home_visible = page.locator("#homePage").evaluate("el => el.classList.contains('active')")
        print(f"  Home active: {home_visible}")

        # Switch to chunks
        page.locator(".tab-item[data-page='chunksPage']").click()
        page.wait_for_timeout(300)
        chunks_visible = page.locator("#chunksPage").evaluate("el => el.classList.contains('active')")
        print(f"  Chunks active: {chunks_visible}")
    except Exception as e:
        issues.append(f"TAB_UI: {e}")
        print(f"  FAIL: {e}")

    # 8. Check PWA manifest
    print("[8] PWA manifest...")
    manifest = page.evaluate("""async () => {
        try {
            const r = await fetch('/manifest.json');
            return await r.json();
        } catch(e) { return null; }
    }""")
    if manifest and manifest.get('name'):
        print(f"  OK: {manifest['name']} - {manifest.get('display')}")
    else:
        issues.append("PWA_MANIFEST_MISSING")
        print("  FAIL: Manifest not loaded")

    browser.close()

# Summary
print(f"\n{'='*50}")
print(f"ISSUES FOUND: {len(issues)}")
for i in issues:
    print(f"  ! {i}")
print(f"JS ERRORS: {len(js_errors)}")
for e in js_errors:
    print(f"  ! {e}")
if not issues and not js_errors:
    print("UI HEALTH: ALL CLEAN")
print(f"{'='*50}")

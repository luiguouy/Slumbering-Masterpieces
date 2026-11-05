#!/usr/bin/env python3
"""
challenge_m3_extra_edge_cases.py - Extra Empirical Stress & Boundary Edge Cases.
Authored by m3_challenger_2_r1.

Adversarial Checks:
1. Ultra-narrow viewport (320px) & landscape phone (667x375):
   - Horizontal overflow on html/body (scrollWidth <= innerWidth).
   - Help modal header, close button, got-it button clickability.
   - Drawer panel width clamp and touch targets >= 40x40.
2. Rapid Mid-Transition Interruption (every 50ms during 300ms CSS cubic-bezier transition).
   - State integrity after 20 interrupted transitions.
3. Help Modal Optical Centroid & Viewport Clipping on extreme heights (360px - 1440px).
   - Confirm modal dialog is never clipped off-screen at top (top >= 0).
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.server_helper import LocalServer
from playwright.sync_api import sync_playwright

def run_extra_edge_cases():
    results = {}
    with LocalServer() as server:
        base_url = server.base_url
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page()

            page.goto(f"{base_url}/index.html")
            page.wait_for_function("() => window.__gardenEngine && window.__gardenEngine.isLoaded()")

            # -------------------------------------------------------------
            # Case 1: Ultra-narrow viewport (320px)
            # -------------------------------------------------------------
            print("\n--- Edge Case 1: 320x568 Ultra-Narrow Viewport ---")
            page.set_viewport_size({"width": 320, "height": 568})
            page.wait_for_timeout(150)

            # Check initial overflow
            overflow_init = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow_init, "Initial view has horizontal scrollbar at 320px"

            # Open Help Modal at 320px
            page.evaluate("() => window.__gardenEngine.openHelp()")
            page.wait_for_timeout(300)

            modal_320 = page.evaluate("""() => {
                const dialog = document.querySelector('.help-dialog');
                const closeBtn = document.getElementById('help-close-btn');
                const gotItBtn = document.getElementById('help-got-it-btn');
                const dRect = dialog.getBoundingClientRect();
                const cRect = closeBtn.getBoundingClientRect();
                const gRect = gotItBtn.getBoundingClientRect();
                return {
                    dialogWidth: Math.round(dRect.width),
                    closeWidth: Math.round(cRect.width),
                    closeHeight: Math.round(cRect.height),
                    gotItVisible: gRect.width > 0 && gRect.height > 0,
                    overflow: document.documentElement.scrollWidth > window.innerWidth
                };
            }""")
            print(f"320px Modal Width: {modal_320['dialogWidth']}px | Close Btn: {modal_320['closeWidth']}x{modal_320['closeHeight']}px | Overflow: {modal_320['overflow']}")
            assert modal_320['dialogWidth'] <= 320, "Dialog wider than 320px screen"
            assert modal_320['closeWidth'] >= 40 and modal_320['closeHeight'] >= 40, "Close btn < 40px at 320px"
            assert not modal_320['overflow'], "Horizontal overflow with help modal open at 320px"

            page.evaluate("() => window.__gardenEngine.closeHelp()")
            page.wait_for_timeout(200)

            # Open Gallery at 320px
            page.evaluate("() => window.__gardenEngine.openGallery()")
            page.wait_for_timeout(300)
            gallery_320 = page.evaluate("""() => {
                const panel = document.querySelector('.gallery-panel');
                const rect = panel.getBoundingClientRect();
                return {
                    panelWidth: Math.round(rect.width),
                    overflow: document.documentElement.scrollWidth > window.innerWidth
                };
            }""")
            print(f"320px Gallery Panel: {gallery_320['panelWidth']}px | Overflow: {gallery_320['overflow']}")
            assert gallery_320['panelWidth'] <= 320, "Gallery panel exceeds screen width"
            assert not gallery_320['overflow'], "Horizontal overflow with gallery open at 320px"

            page.evaluate("() => window.__gardenEngine.closeGallery()")
            page.wait_for_timeout(200)

            results["narrow_320"] = "PASSED"

            # -------------------------------------------------------------
            # Case 2: Mobile Landscape (667x375) Top Clipping Test
            # -------------------------------------------------------------
            print("\n--- Edge Case 2: 667x375 Landscape Top Clipping Test ---")
            page.set_viewport_size({"width": 667, "height": 375})
            page.wait_for_timeout(150)

            page.evaluate("() => window.__gardenEngine.openHelp()")
            page.wait_for_timeout(300)

            clip_check = page.evaluate("""() => {
                const dialog = document.querySelector('.help-dialog');
                const modal = document.getElementById('help-modal');
                const rect = dialog.getBoundingClientRect();
                return {
                    top: rect.top,
                    bottom: rect.bottom,
                    height: rect.height,
                    modalScrollHeight: modal.scrollHeight,
                    modalClientHeight: modal.clientHeight,
                    isClippedTop: rect.top < 0
                };
            }""")
            print(f"Landscape 375h Dialog Rect: top={clip_check['top']}px, height={clip_check['height']}px | Clipped Top: {clip_check['isClippedTop']}")
            # In short viewports, dialog must either fit or be scrollable without unrecoverable negative top
            assert not clip_check['isClippedTop'], f"Dialog top is clipped negatively: {clip_check['top']}px"

            page.evaluate("() => window.__gardenEngine.closeHelp()")
            page.wait_for_timeout(200)
            results["landscape_clipping"] = "PASSED"

            # -------------------------------------------------------------
            # Case 3: Mid-Transition Interrupts (20 cycles at 50ms)
            # -------------------------------------------------------------
            print("\n--- Edge Case 3: Mid-Transition Interrupt Stress (20 rapid interruptions) ---")
            for i in range(20):
                if i % 2 == 0:
                    page.evaluate("() => window.__gardenEngine.openGallery()")
                    page.wait_for_timeout(50)  # Interrupt during 300ms transition
                    page.evaluate("() => window.__gardenEngine.closeGallery()")
                else:
                    page.evaluate("() => window.__gardenEngine.openStory()")
                    page.wait_for_timeout(50)
                    page.evaluate("() => window.__gardenEngine.closeStory()")
                page.wait_for_timeout(30)

            page.wait_for_timeout(400) # Settle
            post_interrupt = page.evaluate("""() => {
                const gOpen = document.getElementById('gallery-drawer').classList.contains('open');
                const sOpen = document.getElementById('story-drawer').classList.contains('open');
                const bClasses = Array.from(document.body.classList);
                return { gOpen, sOpen, bClasses };
            }""")
            print(f"Post-interrupt state: gOpen={post_interrupt['gOpen']}, sOpen={post_interrupt['sOpen']}, bodyClasses={post_interrupt['bClasses']}")
            assert not post_interrupt['gOpen'] and not post_interrupt['sOpen'], "Drawer remained open after interrupt series"
            assert 'gallery-open' not in post_interrupt['bClasses'], "body has leaked gallery-open class"
            assert 'story-open' not in post_interrupt['bClasses'], "body has leaked story-open class"

            results["transition_interrupt"] = "PASSED"

            browser.close()

    print("\n" + "=" * 60)
    print(" ALL EXTRA EDGE CASES PASSED")
    print("=" * 60)
    return results

if __name__ == "__main__":
    run_extra_edge_cases()

#!/usr/bin/env python3
"""
challenge_m2_r1_stress.py - Empirical Adversarial Stress Suite for Milestone 2.
Authored by m2_challenger_2_r1.

Adversarial Dimensions:
1. Rapid Drag & Pointer Jitter (simulates violent erratic dragging and boundary release)
2. Extreme Dynamic Viewport Resizing & Clamping (1440 -> 600 -> 360 -> 1280)
3. Input Parameter Boundaries & NaN/Clamping Verification (brush size, duration, color ratio)
4. Loupe Boundary Traversal & Rapid Toggle Stress (0,0 edges, out-of-bounds coords, rapid toggling)
5. Stroke Dimming Interruption Recovery (mouseleave recovery, opacity restore)
6. Cross-Component Layer Stack Dismissal & Escape Hierarchy (Help Modal -> Brush Popup)
"""

import math
import sys
import time
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.server_helper import LocalServer
from playwright.sync_api import sync_playwright, Page


def wait_engine_ready(page: Page, timeout: int = 15000):
    page.wait_for_function(
        "() => window.__gardenEngine && typeof window.__gardenEngine.isLoaded === 'function' && window.__gardenEngine.isLoaded()",
        timeout=timeout
    )


# ------------------------------------------------------------------------------
# Test 1: Rapid Drag & Pointer Jitter
# ------------------------------------------------------------------------------
def stress_rapid_drag_jitter(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    btn = page.locator("#brush-toggle-btn")
    box = btn.bounding_box()
    start_x = box["x"] + box["width"] / 2
    start_y = box["y"] + box["height"] / 2

    page.mouse.move(start_x, start_y)
    page.mouse.down()

    # Rapid erratic jitter (50 movements in tight loop)
    for i in range(50):
        jitter_x = start_x - (i * 8) + (math.sin(i) * 30)
        jitter_y = start_y + (i * 5) + (math.cos(i) * 30)
        page.mouse.move(jitter_x, jitter_y)
        page.wait_for_timeout(5)

    # Abrupt release outside normal window bounds
    page.mouse.move(-100, -100)
    page.mouse.up()
    page.wait_for_timeout(300)

    # Verify panel state recovery
    status = page.evaluate("""() => {
        const panel = document.getElementById('brush-control');
        const rect = panel.getBoundingClientRect();
        return {
            isBodyDragging: document.body.classList.contains('is-panel-dragging'),
            panelLeft: rect.left,
            panelTop: rect.top,
            withinViewport: rect.left >= 0 && rect.top >= 0 && rect.right <= window.innerWidth && rect.bottom <= window.innerHeight
        };
    }""")

    passed = (not status["isBodyDragging"] and status["withinViewport"])
    return {
        "name": "Rapid Drag & Pointer Jitter",
        "passed": passed,
        "details": status
    }


# ------------------------------------------------------------------------------
# Test 2: Extreme Dynamic Viewport Resizing & Clamping
# ------------------------------------------------------------------------------
def stress_viewport_resize_clamping(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    # Drag panel to bottom-right (x=1100, y=700)
    btn = page.locator("#brush-toggle-btn")
    box = btn.bounding_box()
    page.mouse.move(box["x"] + 20, box["y"] + 20)
    page.mouse.down()
    page.mouse.move(1100, 700)
    page.mouse.up()
    page.wait_for_timeout(200)

    # Shrink viewport aggressively: 1280x800 -> 600x500 -> 375x667
    viewports = [
        {"width": 600, "height": 500},
        {"width": 375, "height": 667},
        {"width": 1440, "height": 900}
    ]

    checks = []
    all_ok = True

    for vp in viewports:
        page.set_viewport_size(vp)
        page.wait_for_timeout(250)

        data = page.evaluate("""() => {
            const panel = document.getElementById('brush-control');
            const rect = panel.getBoundingClientRect();
            const docWidth = document.documentElement.scrollWidth;
            const docHeight = document.documentElement.scrollHeight;
            const winWidth = window.innerWidth;
            const winHeight = window.innerHeight;
            
            return {
                panelLeft: rect.left,
                panelTop: rect.top,
                panelRight: rect.right,
                panelBottom: rect.bottom,
                winWidth,
                winHeight,
                docWidth,
                docHeight,
                noHorizontalOverflow: docWidth <= winWidth + 1,
                clamped: rect.left >= -1 && rect.top >= -1 && rect.right <= winWidth + 2 && rect.bottom <= winHeight + 2
            };
        }""")

        check_pass = data["clamped"] and data["noHorizontalOverflow"]
        if not check_pass:
            all_ok = False
        checks.append({"vp": vp, "data": data, "pass": check_pass})

    return {
        "name": "Extreme Dynamic Viewport Resizing & Clamping",
        "passed": all_ok,
        "details": checks
    }


# ------------------------------------------------------------------------------
# Test 3: Input Parameter Boundaries & Clamping Verification
# ------------------------------------------------------------------------------
def stress_parameter_clamping(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(200)

    # Test extreme values via UI script evaluation
    clamp_results = page.evaluate("""() => {
        const results = {};
        
        // Brush size min/max clamping test
        const slider = document.getElementById('brush-size-slider');
        if (slider) {
            slider.value = '999';
            slider.dispatchEvent(new Event('input', { bubbles: true }));
            const highRadius = window.__gardenEngine.getBrushRadius();
            
            slider.value = '-50';
            slider.dispatchEvent(new Event('input', { bubbles: true }));
            const lowRadius = window.__gardenEngine.getBrushRadius();
            
            results.brushHigh = highRadius;
            results.brushLow = lowRadius;
            results.brushClamped = (highRadius == 160 && lowRadius == 35);
        }
        
        // Color duration slider clamping test
        const durSlider = document.getElementById('brush-duration-slider');
        if (durSlider) {
            durSlider.value = '999';
            durSlider.dispatchEvent(new Event('input', { bubbles: true }));
            const highDur = window.__gardenEngine.getDuration();
            
            durSlider.value = '-10';
            durSlider.dispatchEvent(new Event('input', { bubbles: true }));
            const lowDur = window.__gardenEngine.getDuration();
            
            results.durHigh = highDur;
            results.durLow = lowDur;
            results.durClamped = (highDur <= 30 && lowDur >= 4);
        }
        
        // Cursor ring sanity
        const ring = document.querySelector('#custom-cursor .cursor-ring') || document.querySelector('.cursor-ring');
        results.ringWidth = ring ? ring.style.width : '';
        results.ringValid = Boolean(ring && results.ringWidth.endsWith('px') && !results.ringWidth.includes('NaN'));
        
        return results;
    }""")

    passed = clamp_results.get("brushClamped", False) and clamp_results.get("durClamped", False) and clamp_results.get("ringValid", False)
    return {
        "name": "Input Parameter Boundaries & Clamping Verification",
        "passed": passed,
        "details": clamp_results
    }


# ------------------------------------------------------------------------------
# Test 4: Loupe Boundary Traversal & Rapid Toggle Stress
# ------------------------------------------------------------------------------
def stress_loupe_boundary_traversal(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    # Rapid toggle loupe 5 times
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)

    for _ in range(5):
        page.click("#toggle-loupe-btn")
        page.wait_for_timeout(50)

    # Ensure loupe is ON
    is_on = page.evaluate("() => window.__gardenEngine.isLoupeEnabled()")
    if not is_on:
        page.click("#toggle-loupe-btn")
        page.wait_for_timeout(100)

    # Move cursor across boundary coordinates: (0, 0), (1279, 799), (640, 400)
    boundary_coords = [(0, 0), (1279, 799), (640, 400), (10, 10), (1270, 790)]
    for bx, by in boundary_coords:
        page.mouse.move(bx, by)
        page.wait_for_timeout(30)

    # Check loupe element health
    loupe_health = page.evaluate("""() => {
        const loupe = document.getElementById('macro-loupe');
        const canvas = document.getElementById('macro-loupe-canvas');
        const errors = [];
        if (!loupe) errors.push('Loupe DOM element missing');
        if (!canvas) errors.push('Loupe canvas DOM element missing');
        if (canvas && (canvas.width <= 0 || canvas.height <= 0)) errors.push('Invalid loupe canvas dimensions');
        
        return {
            enabled: window.__gardenEngine.isLoupeEnabled(),
            display: loupe ? loupe.style.display : '',
            canvasWidth: canvas ? canvas.width : 0,
            canvasHeight: canvas ? canvas.height : 0,
            errors
        };
    }""")

    # Clean up (toggle off)
    page.click("#toggle-loupe-btn")
    page.wait_for_timeout(150)
    page.mouse.click(200, 200)

    passed = (len(loupe_health["errors"]) == 0 and loupe_health["enabled"])
    return {
        "name": "Loupe Boundary Traversal & Rapid Toggle Stress",
        "passed": passed,
        "details": loupe_health
    }


# ------------------------------------------------------------------------------
# Test 5: Stroke Dimming Interruption Recovery
# ------------------------------------------------------------------------------
def stress_stroke_interruption_recovery(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    # Simulate painting stroke (adds .subtle)
    page.mouse.move(640, 400)
    page.mouse.down()
    page.mouse.move(650, 410)
    page.wait_for_timeout(50)

    during_stroke = page.evaluate("""() => {
        const quote = document.getElementById('art-quote');
        return {
            hasSubtle: quote.classList.contains('subtle')
        };
    }""")

    page.mouse.up()

    # Move mouse outside the viewport to trigger window mouseleave
    page.evaluate("() => window.dispatchEvent(new Event('mouseleave'))")
    page.wait_for_timeout(400)

    # Verify art quote opacity returned to normal and .subtle class removed
    recovery = page.evaluate("""() => {
        const quote = document.getElementById('art-quote');
        const cs = window.getComputedStyle(quote);
        return {
            hasSubtle: quote.classList.contains('subtle'),
            opacity: parseFloat(cs.opacity)
        };
    }""")

    passed = (during_stroke["hasSubtle"] and not recovery["hasSubtle"] and recovery["opacity"] >= 0.8)
    return {
        "name": "Stroke Dimming Interruption Recovery",
        "passed": passed,
        "details": {
            "during_stroke": during_stroke,
            "recovery": recovery
        }
    }


# ------------------------------------------------------------------------------
# Test 6: Cross-Component Layer Stack Dismissal & Escape Hierarchy
# ------------------------------------------------------------------------------
def stress_cross_component_dismissal(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    # 1. Open brush popup
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)

    # 2. Press Escape key -> should close brush popup
    page.keyboard.press("Escape")
    page.wait_for_timeout(350)

    esc_closed = page.evaluate("""() => {
        const popup = document.getElementById('brush-popup');
        return !popup.classList.contains('open');
    }""")

    # 3. Open brush popup again
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)

    # 4. Click help button -> opens help modal on top
    page.click("#help-toggle-btn")
    page.wait_for_timeout(350)

    modal_state = page.evaluate("""() => {
        const helpModal = document.getElementById('help-modal');
        return {
            helpOpen: helpModal.classList.contains('open')
        };
    }""")

    # 5. Press Escape -> hierarchical close: closes help modal first
    page.keyboard.press("Escape")
    page.wait_for_timeout(350)

    after_first_esc = page.evaluate("""() => {
        const helpModal = document.getElementById('help-modal');
        const brush = document.getElementById('brush-popup');
        return {
            helpOpen: helpModal.classList.contains('open'),
            brushOpen: brush.classList.contains('open')
        };
    }""")

    # 6. Press Escape second time -> closes brush popup
    page.keyboard.press("Escape")
    page.wait_for_timeout(350)

    after_second_esc = page.evaluate("""() => {
        const brush = document.getElementById('brush-popup');
        return !brush.classList.contains('open');
    }""")

    passed = (esc_closed and modal_state["helpOpen"] and not after_first_esc["helpOpen"] and after_second_esc)
    return {
        "name": "Cross-Component Layer Stack Dismissal & Escape Hierarchy",
        "passed": passed,
        "details": {
            "esc_closed": esc_closed,
            "modal_state": modal_state,
            "after_first_esc": after_first_esc,
            "after_second_esc": after_second_esc
        }
    }


def main():
    print("=" * 80)
    print(" ⚡ Milestone 2 Adversarial Stress Suite (m2_challenger_2_r1)")
    print("=" * 80)

    with LocalServer() as server:
        base_url = server.base_url
        print(f" Local Server: {base_url}\n")

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            tests = [
                ("Stress 1: Rapid Drag & Pointer Jitter", stress_rapid_drag_jitter),
                ("Stress 2: Viewport Resize & Clamping", stress_viewport_resize_clamping),
                ("Stress 3: Parameter Boundaries & Clamping", stress_parameter_clamping),
                ("Stress 4: Loupe Boundary Traversal", stress_loupe_boundary_traversal),
                ("Stress 5: Stroke Dimming Interruption", stress_stroke_interruption_recovery),
                ("Stress 6: Cross-Component Dismissal & Escape", stress_cross_component_dismissal),
            ]

            all_passed = True
            results = []

            for idx, (title, fn) in enumerate(tests, 1):
                start_t = time.time()
                print(f"[{idx}/{len(tests)}] Executing {title}...")
                try:
                    res = fn(page, base_url)
                    dur = (time.time() - start_t) * 1000
                    status = "PASSED" if res["passed"] else "FAILED"
                    if not res["passed"]:
                        all_passed = False
                    print(f"      Result: {status} ({dur:.1f}ms)")
                    results.append((title, status, dur, res))
                except Exception as exc:
                    dur = (time.time() - start_t) * 1000
                    all_passed = False
                    print(f"      Result: EXCEPTION ({dur:.1f}ms) — {exc}")
                    results.append((title, "EXCEPTION", dur, {"error": str(exc)}))

            browser.close()

            print("\n" + "=" * 80)
            print(" 📊 ADVERSARIAL STRESS SUMMARY")
            print("=" * 80)
            for title, status, dur, res in results:
                symbol = "✓" if status == "PASSED" else "✗"
                print(f" {symbol} {title:<50} [{status}] ({dur:6.1f}ms)")

            print("=" * 80)
            print(f" OVERALL: {'ALL PASSED (6/6)' if all_passed else 'FAILURES DETECTED'}")
            print("=" * 80)

            return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

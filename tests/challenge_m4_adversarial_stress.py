#!/usr/bin/env python3
"""
challenge_m4_adversarial_stress.py - Empirical Adversarial Stress Suite for Milestone 4.
Authored by: m4_challenger_2 (Adversarial Stress & Interaction Specialist)

Adversarial Dimensions:
1. 15-Viewport Responsive Sweep & Zero Horizontal Scroll Leak (320px to 2560px)
2. Dynamic Viewport Resizing During Active Overlays (Gallery, Story, Help)
3. CSS Token Purity & Syntax Validation (0 bare raw hex outside var(), balance/pretty wrapping)
4. High-Frequency Multi-Layer State Thrashing & Gesture Chaos
"""

import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

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
# Test 1: 15-Viewport Responsive Sweep & Zero Horizontal Overflow Leak
# ------------------------------------------------------------------------------
def test_viewport_sweep_overflow_leak(page: Page, base_url: str) -> Dict[str, Any]:
    viewports = [
        (320, 568, "Mobile Minimum (SE 1st gen)"),
        (360, 640, "Android Compact"),
        (375, 667, "iPhone SE 2/3 / Mobile Standard"),
        (390, 844, "iPhone 12/13/14 Pro"),
        (414, 896, "iPhone Plus/XR"),
        (480, 800, "Mobile Large Landscape / Handheld"),
        (640, 1024, "Cascade Boundary 640px (Tier 4B)"),
        (641, 1024, "Cascade Boundary 641px (Tier 3)"),
        (768, 1024, "iPad Portrait / Tablet Standard"),
        (800, 1280, "Tablet Medium"),
        (1024, 768, "iPad Landscape / Desktop Compact"),
        (1280, 800, "Desktop Standard (WXGA)"),
        (1440, 900, "Desktop Large / MacBook Pro"),
        (1920, 1080, "Full HD Widescreen"),
        (2560, 1440, "2K Ultra-Wide")
    ]

    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    sweep_results = []
    failures = []

    for w, h, label in viewports:
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(100)

        leak_data = page.evaluate("""() => {
            const doc = document.documentElement;
            const body = document.body;
            const vw = window.innerWidth;
            
            const docScrollW = doc.scrollWidth;
            const bodyScrollW = body.scrollWidth;
            
            // Check bounding boxes of floating HUD elements
            const msw = document.getElementById('mode-switcher');
            const help = document.querySelector('.help-trigger-wrap') || document.getElementById('help-toggle-btn');
            const brush = document.getElementById('brush-control');
            
            const mswRect = msw ? msw.getBoundingClientRect() : null;
            const helpRect = help ? help.getBoundingClientRect() : null;
            const brushRect = brush ? brush.getBoundingClientRect() : null;
            
            const mswInBounds = mswRect ? (mswRect.left >= 0 && mswRect.right <= vw + 1) : true;
            const helpInBounds = helpRect ? (helpRect.left >= 0 && helpRect.right <= vw + 1) : true;
            const brushInBounds = brushRect ? (brushRect.left >= -5 && brushRect.right <= vw + 5) : true;
            
            return {
                vw,
                docScrollW,
                bodyScrollW,
                hasOverflow: (docScrollW > vw) || (bodyScrollW > vw),
                mswInBounds,
                helpInBounds,
                brushInBounds
            };
        }""")

        passed = (not leak_data["hasOverflow"] and
                  leak_data["mswInBounds"] and
                  leak_data["helpInBounds"])

        item = {
            "viewport": f"{w}x{h}",
            "label": label,
            "passed": passed,
            "data": leak_data
        }
        sweep_results.append(item)
        if not passed:
            failures.append(item)

    return {
        "name": "15-Viewport Sweep & Zero Horizontal Overflow Leak",
        "passed": len(failures) == 0,
        "total_viewports": len(viewports),
        "failures_count": len(failures),
        "failures": failures
    }


# ------------------------------------------------------------------------------
# Test 2: Dynamic Viewport Resizing During Active Overlays
# ------------------------------------------------------------------------------
def test_dynamic_resize_with_active_overlays(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(200)

    checks = []

    # 1. Gallery Drawer Active Resize Test
    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(350)

    # Sequence of rapid viewport resizes
    resize_steps = [
        (1440, 900, 3),  # 3 cols
        (1024, 768, 3),  # 3 cols
        (800, 600, 2),   # 2 cols
        (640, 1024, 1),  # 1 col (folding boundary)
        (375, 667, 1),   # 1 col mobile
        (1280, 800, 3)   # restore to 3 cols
    ]

    gallery_resize_ok = True
    for w, h, exp_cols in resize_steps:
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(100)

        grid_info = page.evaluate("""() => {
            const container = document.getElementById('gallery-list-container');
            const cs = window.getComputedStyle(container);
            const cols = cs.gridTemplateColumns.split(' ').filter(x => x.length > 0).length;
            const cards = document.querySelectorAll('.gallery-card');
            return {
                cols,
                cardCount: cards.length,
                overflow: document.documentElement.scrollWidth > window.innerWidth
            };
        }""")

        if grid_info["cols"] != exp_cols or grid_info["overflow"]:
            gallery_resize_ok = False
            checks.append({
                "phase": f"gallery_resize_{w}x{h}",
                "pass": False,
                "expected_cols": exp_cols,
                "got_cols": grid_info["cols"],
                "overflow": grid_info["overflow"]
            })

    checks.append({
        "phase": "gallery_active_resize_cascade",
        "pass": gallery_resize_ok
    })

    page.evaluate("() => window.__gardenEngine.closeGallery()")
    page.wait_for_timeout(250)

    # 2. Story Drawer Active Resize Test
    page.evaluate("() => window.__gardenEngine.openStory()")
    page.wait_for_timeout(350)

    story_steps = [
        (1440, 900, "side_panel"),
        (768, 1024, "side_panel"),
        (640, 900, "bottom_sheet"),
        (375, 667, "bottom_sheet"),
        (1280, 800, "side_panel")
    ]

    story_resize_ok = True
    for w, h, expected_layout in story_steps:
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(100)

        story_info = page.evaluate("""() => {
            const panel = document.querySelector('.story-panel');
            if (!panel) return { exists: false };
            const rect = panel.getBoundingClientRect();
            const vw = window.innerWidth;
            const vh = window.innerHeight;
            
            // Bottom sheet is full width at bottom
            const isBottomSheet = (rect.width >= vw - 1) && (rect.bottom >= vh - 2);
            return {
                exists: true,
                width: rect.width,
                bottom: rect.bottom,
                isBottomSheet,
                overflow: document.documentElement.scrollWidth > vw
            };
        }""")

        if not story_info.get("exists", False):
            story_resize_ok = False
            checks.append({"phase": f"story_resize_{w}x{h}", "pass": False, "error": "story-panel not found"})
            continue

        layout_matched = (story_info["isBottomSheet"] if expected_layout == "bottom_sheet" else not story_info["isBottomSheet"])
        if not layout_matched or story_info["overflow"]:
            story_resize_ok = False
            checks.append({
                "phase": f"story_resize_{w}x{h}",
                "pass": False,
                "expected": expected_layout,
                "actual": "bottom_sheet" if story_info["isBottomSheet"] else "side_panel",
                "overflow": story_info["overflow"]
            })

    checks.append({
        "phase": "story_active_resize_cascade",
        "pass": story_resize_ok
    })

    page.evaluate("() => window.__gardenEngine.closeStory()")
    page.wait_for_timeout(250)

    # 3. Help Modal Active Resize Test
    page.evaluate("() => window.__gardenEngine.openHelp()")
    page.wait_for_timeout(350)

    help_steps = [1920, 1440, 1280, 768, 480, 375]
    help_resize_ok = True
    for w in help_steps:
        page.set_viewport_size({"width": w, "height": 800})
        page.wait_for_timeout(100)

        help_data = page.evaluate("""() => {
            const dialog = document.querySelector('.help-dialog');
            const closeBtn = document.getElementById('help-close-btn');
            const rect = dialog.getBoundingClientRect();
            const btnRect = closeBtn.getBoundingClientRect();
            const vw = window.innerWidth;
            const vh = window.innerHeight;
            
            const centroidRatio = (rect.top + rect.height / 2) / vh;
            return {
                width: rect.width,
                inViewport: rect.left >= 0 && rect.right <= vw,
                closeBtnSize: btnRect.width >= 40 && btnRect.height >= 40,
                centroidRatio,
                overflow: document.documentElement.scrollWidth > vw
            };
        }""")

        if not help_data["inViewport"] or not help_data["closeBtnSize"] or help_data["overflow"]:
            help_resize_ok = False
            checks.append({
                "phase": f"help_resize_{w}px",
                "pass": False,
                "data": help_data
            })

    checks.append({
        "phase": "help_active_resize_cascade",
        "pass": help_resize_ok
    })

    page.evaluate("() => window.__gardenEngine.closeHelp()")
    page.wait_for_timeout(250)

    all_passed = all(c["pass"] for c in checks)
    return {
        "name": "Dynamic Viewport Resizing During Active Overlays",
        "passed": all_passed,
        "details": checks
    }


# ------------------------------------------------------------------------------
# Test 3: CSS Token Purity & Syntax Validation
# ------------------------------------------------------------------------------
def test_css_token_purity_and_syntax() -> Dict[str, Any]:
    style_path = PROJECT_ROOT / "style.css"
    content = style_path.read_text(encoding="utf-8")

    # Strip comments from content
    no_comments = re.sub(r"/\*[\s\S]*?\*/", "", content)

    # Locate :root
    root_match = re.search(r":root\s*\{[^}]+\}", no_comments)
    no_root = no_comments[root_match.end():] if root_match else no_comments

    # Strip valid var(--token, #hex) fallback patterns
    no_var_fallbacks = re.sub(r"var\s*\(\s*--[\w-]+\s*,\s*#[0-9a-fA-F]+\s*\)", "var(--token)", no_root)

    # Now verify that NO bare raw hex color values remain outside :root
    hex_pattern = re.compile(r"#[0-9a-fA-F]{3,8}\b")
    bare_hex_matches = hex_pattern.findall(no_var_fallbacks)

    # Check text-wrap rules
    has_text_wrap_balance = "text-wrap: balance" in content
    has_text_wrap_pretty = "text-wrap: pretty" in content

    # Check utility classes
    has_grid_cols_12 = ".grid-cols-12" in content
    has_grid_cols_1 = ".grid-cols-1" in content
    has_swiss_grid_cascade = ".swiss-grid-cascade" in content

    # Check balanced braces in CSS
    open_braces = content.count("{")
    close_braces = content.count("}")
    braces_balanced = (open_braces == close_braces)

    passed = (len(bare_hex_matches) == 0 and
              has_text_wrap_balance and
              has_text_wrap_pretty and
              has_grid_cols_12 and
              has_grid_cols_1 and
              has_swiss_grid_cascade and
              braces_balanced)

    return {
        "name": "CSS Token Purity & Syntax Validation",
        "passed": passed,
        "bare_raw_hex_count": len(bare_hex_matches),
        "bare_raw_hex_matches": bare_hex_matches,
        "has_text_wrap_balance": has_text_wrap_balance,
        "has_text_wrap_pretty": has_text_wrap_pretty,
        "has_grid_cols_12": has_grid_cols_12,
        "has_grid_cols_1": has_grid_cols_1,
        "has_swiss_grid_cascade": has_swiss_grid_cascade,
        "braces_balanced": braces_balanced,
        "open_braces": open_braces,
        "close_braces": close_braces
    }


# ------------------------------------------------------------------------------
# Test 4: High-Frequency Chaotic Painting & Multi-Overlay Thrashing
# ------------------------------------------------------------------------------
def test_chaotic_painting_and_overlay_thrashing(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    console_errors = []
    page_errors = []

    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" and "favicon.ico" not in m.text else None)
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    # Paint 10 strokes across stage while rapidly alternating sleep and scratch modes
    stage_box = page.locator("#art-stage").bounding_box()
    cx = stage_box["x"] + stage_box["width"] / 2
    cy = stage_box["y"] + stage_box["height"] / 2

    for cycle in range(5):
        # Alternate mode
        if cycle % 2 == 0:
            page.click("#msw-scratch-btn")
        else:
            page.click("#msw-sleep-btn")

        # Rapid stroke
        page.mouse.move(cx - 100, cy - 50 + cycle * 20)
        page.mouse.down()
        for s in range(5):
            page.mouse.move(cx - 100 + s * 40, cy - 50 + cycle * 20 + (s % 2) * 15)
            page.wait_for_timeout(10)
        page.mouse.up()

        # Interleaved overlay toggle
        if cycle == 1:
            page.keyboard.press("g")  # open gallery
            page.wait_for_timeout(60)
            page.keyboard.press("Escape")  # close gallery
        elif cycle == 3:
            page.keyboard.press("s")  # open story
            page.wait_for_timeout(60)
            page.keyboard.press("Escape")  # close story

    page.wait_for_timeout(400)

    # Audit engine state and canvas stability
    engine_state = page.evaluate("""() => {
        return {
            isLoaded: window.__gardenEngine.isLoaded(),
            appMode: window.__gardenEngine.getAppMode(),
            hasCanvas: !!document.getElementById('bg-canvas'),
            isLoupeActive: window.__gardenEngine.isLoupeEnabled()
        };
    }""")

    passed = (len(console_errors) == 0 and
              len(page_errors) == 0 and
              engine_state["isLoaded"] and
              engine_state["hasCanvas"])

    return {
        "name": "High-Frequency Chaotic Painting & Multi-Overlay Thrashing",
        "passed": passed,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "engine_state": engine_state
    }


# ------------------------------------------------------------------------------
# Main Runner
# ------------------------------------------------------------------------------
def main():
    print("=" * 80)
    print(" ⚡ Milestone 4 Empirical Adversarial Stress Suite (m4_challenger_2)")
    print("=" * 80)

    results = []
    all_passed = True

    # 1. Static CSS Token & Syntax Validation (no server needed)
    print("[1/4] Executing CSS Token Purity & Syntax Validation...")
    t0 = time.time()
    res1 = test_css_token_purity_and_syntax()
    dur1 = (time.time() - t0) * 1000
    status1 = "PASSED" if res1["passed"] else "FAILED"
    if not res1["passed"]:
        all_passed = False
    print(f"      Result: {status1} ({dur1:.1f}ms)")
    results.append((res1["name"], status1, dur1, res1))

    # 2. Browser Tests
    with LocalServer() as server:
        base_url = server.base_url
        print(f"\n Local Server: {base_url}\n")

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            browser_tests = [
                ("[2/4] Viewport Sweep & Zero Overflow Leak", test_viewport_sweep_overflow_leak),
                ("[3/4] Dynamic Viewport Resizing During Overlays", test_dynamic_resize_with_active_overlays),
                ("[4/4] Chaotic Painting & Overlay Thrashing", test_chaotic_painting_and_overlay_thrashing)
            ]

            for label, fn in browser_tests:
                print(f"{label}...")
                start_t = time.time()
                try:
                    res = fn(page, base_url)
                    dur = (time.time() - start_t) * 1000
                    status = "PASSED" if res["passed"] else "FAILED"
                    if not res["passed"]:
                        all_passed = False
                    print(f"      Result: {status} ({dur:.1f}ms)")
                    results.append((res["name"], status, dur, res))
                except Exception as exc:
                    dur = (time.time() - start_t) * 1000
                    all_passed = False
                    print(f"      Result: EXCEPTION ({dur:.1f}ms) — {exc}")
                    results.append((label, "EXCEPTION", dur, {"error": str(exc)}))

            browser.close()

    print("\n" + "=" * 80)
    print(" 📊 M4 ADVERSARIAL STRESS SUMMARY")
    print("=" * 80)
    for title, status, dur, res in results:
        symbol = "✓" if status == "PASSED" else "✗"
        print(f" {symbol} {title:<55} [{status}] ({dur:6.1f}ms)")

    print("=" * 80)
    print(f" OVERALL VERDICT: {'APPROVE (All 4/4 Passed)' if all_passed else 'REQUEST_CHANGES (Failures Detected)'}")
    print("=" * 80)

    # Save results to agent metadata directory
    report_file = PROJECT_ROOT / ".agents" / "teamwork" / "m4_challenger_2" / "challenge_m4_results.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.time(),
            "overall_passed": all_passed,
            "results": [r[3] for r in results]
        }, f, indent=2, ensure_ascii=False)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

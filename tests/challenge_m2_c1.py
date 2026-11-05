#!/usr/bin/env python3
"""
challenge_m2_c1.py - Empirical Adversarial Stress Harness for Milestone 2.

Author: m2_challenger_1 (EMPIRICAL CHALLENGER)
Target: Milestone 2: Floating Controls & Art Stage Alignment
Authoritative Scope:
- PROJECT.md (Features 4, 5, 6)
- ORIGINAL_REQUEST.md
- DISPATCH.md

Evaluates:
1. Challenge 1: Bottom Baseline Alignment Rigor (0.00px diff across desktop and mobile)
2. Challenge 2: Optical Center Ratio (Y_center / H in [0.440, 0.460] across viewports and quote lengths)
3. Challenge 3: Reading Measure Bounds & Typography Closures across viewports
4. Challenge 4: Elevation Hierarchy & Capsule Separation Analysis
5. Challenge 5: Brush Control Panel, Draggable Coordinates & Loupe Safety Invariants
"""

import math
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


# ==============================================================================
# Challenge 1: Bottom Baseline Alignment Rigor Across Viewports
# ==============================================================================
def challenge_baseline_alignment(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test bottom baseline alignment between #mode-switcher and .help-trigger-wrap / #help-toggle-btn.
    The bottom edge offset (window.innerHeight - rect.bottom) must be identical (0.00px difference).
    """
    viewports = [
        {"w": 2560, "h": 1440, "name": "2560x1440 (Widescreen 2K)", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 1920, "h": 1080, "name": "1920x1080 (Desktop FHD)", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 1440, "h": 900,  "name": "1440x900 (MacBook 14\")", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 1366, "h": 768,  "name": "1366x768 (Standard Laptop)", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 1280, "h": 800,  "name": "1280x800 (Compact WXGA)", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 1024, "h": 768,  "name": "1024x768 (iPad Landscape)", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 1023, "h": 768,  "name": "1023x768 (Tablet Large)", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 768,  "h": 1024, "name": "768x1024 (iPad Portrait)", "expected_bottom": 24.0, "is_mobile": False},
        {"w": 767,  "h": 900,  "name": "767x900 (Mobile Boundary)", "expected_bottom": 16.0, "is_mobile": True},
        {"w": 414,  "h": 896,  "name": "414x896 (iPhone XR / 11)", "expected_bottom": 16.0, "is_mobile": True},
        {"w": 390,  "h": 844,  "name": "390x844 (iPhone 12 / 13 / 14)", "expected_bottom": 16.0, "is_mobile": True},
        {"w": 375,  "h": 667,  "name": "375x667 (iPhone SE / 8)", "expected_bottom": 16.0, "is_mobile": True},
        {"w": 320,  "h": 568,  "name": "320x568 (iPhone 5 / Narrow)", "expected_bottom": 16.0, "is_mobile": True},
    ]

    results = []
    failures = []

    for vp in viewports:
        page.set_viewport_size({"width": vp["w"], "height": vp["h"]})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        page.wait_for_timeout(100)

        metrics = page.evaluate("""() => {
            const switcher = document.getElementById('mode-switcher');
            const helpWrap = document.querySelector('.help-trigger-wrap');
            const helpBtn = document.getElementById('help-toggle-btn');

            const sRect = switcher.getBoundingClientRect();
            const hwRect = helpWrap ? helpWrap.getBoundingClientRect() : null;
            const hbRect = helpBtn ? helpBtn.getBoundingClientRect() : null;

            const winH = window.innerHeight;
            const sBottomOffset = winH - sRect.bottom;
            const hwBottomOffset = hwRect ? winH - hwRect.bottom : null;
            const hbBottomOffset = hbRect ? winH - hbRect.bottom : null;

            return {
                winH,
                sRect: { top: sRect.top, bottom: sRect.bottom, height: sRect.height },
                hwRect: hwRect ? { top: hwRect.top, bottom: hwRect.bottom, height: hwRect.height } : null,
                hbRect: hbRect ? { top: hbRect.top, bottom: hbRect.bottom, height: hbRect.height } : null,
                sBottomOffset,
                hwBottomOffset,
                hbBottomOffset,
                diffWithWrap: hwBottomOffset !== null ? Math.abs(sBottomOffset - hwBottomOffset) : null,
                diffWithBtn: hbBottomOffset !== null ? Math.abs(sBottomOffset - hbBottomOffset) : null
            };
        }""")

        diff = metrics["diffWithWrap"] if metrics["diffWithWrap"] is not None else metrics["diffWithBtn"]
        is_exact_zero = diff is not None and diff <= 0.05
        expected_b = vp["expected_bottom"]
        matches_expected = abs(metrics["sBottomOffset"] - expected_b) <= 1.0

        item = {
            "viewport": vp["name"],
            "w": vp["w"],
            "h": vp["h"],
            "switcher_bottom": metrics["sBottomOffset"],
            "help_bottom": metrics["hwBottomOffset"],
            "diff": diff,
            "is_exact_zero": is_exact_zero,
            "matches_expected": matches_expected
        }
        results.append(item)

        if not is_exact_zero:
            failures.append(f"{vp['name']}: bottom difference {diff:.3f}px > 0.05px (Switcher={metrics['sBottomOffset']:.2f}px, Help={metrics['hwBottomOffset']:.2f}px)")
        elif not matches_expected:
            failures.append(f"{vp['name']}: expected bottom {expected_b}px but got Switcher={metrics['sBottomOffset']:.2f}px")

    # Interactive state test
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    interactive_diff = page.evaluate("""() => {
        const scratchBtn = document.getElementById('msw-scratch-btn');
        const switcher = document.getElementById('mode-switcher');
        const helpWrap = document.querySelector('.help-trigger-wrap');

        const beforeOffset = window.innerHeight - switcher.getBoundingClientRect().bottom;
        scratchBtn.click();
        const afterScratchOffset = window.innerHeight - switcher.getBoundingClientRect().bottom;

        const sleepBtn = document.getElementById('msw-sleep-btn');
        sleepBtn.click();
        const afterSleepOffset = window.innerHeight - switcher.getBoundingClientRect().bottom;

        const helpOffset = window.innerHeight - helpWrap.getBoundingClientRect().bottom;

        return {
            beforeOffset,
            afterScratchOffset,
            afterSleepOffset,
            helpOffset,
            driftScratch: Math.abs(afterScratchOffset - beforeOffset),
            driftSleep: Math.abs(afterSleepOffset - beforeOffset),
            diffHelp: Math.abs(afterSleepOffset - helpOffset)
        };
    }""")

    if interactive_diff["driftScratch"] > 0.01 or interactive_diff["driftSleep"] > 0.01:
        failures.append(f"Interactive state transition caused baseline drift: scratch={interactive_diff['driftScratch']}px, sleep={interactive_diff['driftSleep']}px")

    return {
        "passed": len(failures) == 0,
        "total_viewports": len(viewports),
        "results": results,
        "interactive_check": interactive_diff,
        "failures_count": len(failures),
        "failures": failures
    }


# ==============================================================================
# Challenge 2: Optical Center Ratio (Y_center / H in [0.440, 0.460])
# ==============================================================================
def challenge_optical_center_ratio(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test optical center ratio for .art-quote-container:
    Y_center / H must strictly belong to [0.440, 0.460] (target 0.450).
    Tested under:
    - 1920x1080, 1440x900, 1280x800, 768x1024 (as specified in DISPATCH)
    - plus 2560x1440, 1024x768, 375x667, 320x568
    - and across diverse quote lengths (short, long, CJK, multi-line).
    """
    dispatch_viewports = [
        {"w": 1920, "h": 1080, "name": "1920x1080"},
        {"w": 1440, "h": 900,  "name": "1440x900"},
        {"w": 1280, "h": 800,  "name": "1280x800"},
        {"w": 768,  "h": 1024, "name": "768x1024"},
        {"w": 2560, "h": 1440, "name": "2560x1440"},
        {"w": 1024, "h": 768,  "name": "1024x768"},
        {"w": 375,  "h": 667,  "name": "375x667"},
        {"w": 320,  "h": 568,  "name": "320x568"}
    ]

    viewport_results = []
    failures = []

    for vp in dispatch_viewports:
        page.set_viewport_size({"width": vp["w"], "height": vp["h"]})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        page.wait_for_timeout(100)

        data = page.evaluate("""() => {
            const quote = document.getElementById('art-quote');
            const rect = quote.getBoundingClientRect();
            const centerY = rect.top + rect.height / 2;
            const ratio = centerY / window.innerHeight;
            return {
                top: rect.top,
                height: rect.height,
                centerY,
                winH: window.innerHeight,
                ratio
            };
        }""")

        ratio = data["ratio"]
        valid = 0.440 <= ratio <= 0.460
        viewport_results.append({
            "viewport": vp["name"],
            "ratio": ratio,
            "centerY": data["centerY"],
            "winH": data["winH"],
            "valid": valid
        })

        if not valid:
            failures.append(f"Viewport {vp['name']}: optical center ratio {ratio:.4f} outside [0.440, 0.460]")

    # Adversarial Quote Stress: Test diverse quote texts
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    stress_quotes = [
        {"desc": "Short 1-line quote", "text": "“Art is life.”", "author": "— Unknown"},
        {"desc": "Medium quote (Default)", "text": "“Simplicity is the ultimate sophistication.”", "author": "— Leonardo da Vinci"},
        {"desc": "Long CJK quote", "text": "“水光潋滟晴方好，山色空蒙雨亦奇。欲把西湖比西子，淡妆浓抹总相宜。”", "author": "— 苏轼 (Song Dynasty)"},
        {"desc": "Multi-line English quote", "text": "“I don't know anything with certainty, but seeing the stars makes me dream. There is nothing more truly artistic than to love people.”", "author": "— Vincent van Gogh"},
        {"desc": "Very long philosophical quote", "text": "“The painter has the Universe in his mind and hands. Where the spirit does not work with the hand, there is no art. Principles for the development of a complete mind: study the art of science; study the science of art.”", "author": "— Leonardo da Vinci"}
    ]

    quote_results = []
    for q in stress_quotes:
        res = page.evaluate("""(q) => {
            const textEl = document.querySelector('#art-quote .quote-text');
            const authorEl = document.querySelector('#art-quote .quote-author');
            const quote = document.getElementById('art-quote');

            textEl.textContent = q.text;
            authorEl.textContent = q.author;

            const rect = quote.getBoundingClientRect();
            const centerY = rect.top + rect.height / 2;
            const ratio = centerY / window.innerHeight;

            return {
                height: rect.height,
                width: rect.width,
                centerY,
                ratio
            };
        }""", q)

        valid = 0.440 <= res["ratio"] <= 0.460
        quote_results.append({
            "desc": q["desc"],
            "height": res["height"],
            "width": res["width"],
            "ratio": res["ratio"],
            "valid": valid
        })

        if not valid:
            failures.append(f"Quote stress '{q['desc']}': ratio {res['ratio']:.4f} outside [0.440, 0.460]")

    return {
        "passed": len(failures) == 0,
        "viewports_evaluated": len(dispatch_viewports),
        "viewport_results": viewport_results,
        "quote_stress_results": quote_results,
        "failures_count": len(failures),
        "failures": failures
    }


# ==============================================================================
# Challenge 3: Reading Measure Bounds & Typography Closures
# ==============================================================================
def challenge_reading_measure_and_typography(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test reading measure:
    - Width constraint: max-width <= min(768px, 65ch, 100vw - 64px) on desktop (< 840px on widescreen >= 1440px)
    - Zero horizontal overflow
    - Typographic line-height closure to 24px baseline modular units
    """
    viewports = [(1920, 1080), (1440, 900), (1024, 768), (768, 1024), (375, 667)]
    results = []
    failures = []

    for w, h in viewports:
        page.set_viewport_size({"width": w, "height": h})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        page.wait_for_timeout(100)

        batch_res = page.evaluate("""() => {
            const quote = document.getElementById('art-quote');
            const textEl = document.querySelector('#art-quote .quote-text');
            const authorEl = document.querySelector('#art-quote .quote-author');
            const cs = window.getComputedStyle(quote);
            const csText = window.getComputedStyle(textEl);
            const csAuthor = window.getComputedStyle(authorEl);

            const winW = window.innerWidth;
            const docW = document.documentElement.scrollWidth;
            const quoteRect = quote.getBoundingClientRect();

            const textLh = parseFloat(csText.lineHeight);
            const textMb = parseFloat(csText.marginBottom);
            const authorLh = parseFloat(csAuthor.lineHeight);

            const hasOverflow = docW > winW;
            const maxAllowedW = winW >= 1440 ? 840.5 : 768.5;
            const exceedsMaxWidth = quoteRect.width > maxAllowedW;
            const safeMargin = winW <= 767 ? 32 : (winW >= 1440 ? 128 : 64);
            const exceedsViewportSafe = quoteRect.width > (winW - safeMargin + 1.0);

            return {
                winW,
                docW,
                quoteW: quoteRect.width,
                textLh,
                textMb,
                authorLh,
                hasOverflow,
                exceedsMaxWidth,
                exceedsViewportSafe
            };
        }""")

        results.append({"viewport": f"{w}x{h}", **batch_res})

        if batch_res["hasOverflow"]:
            failures.append(f"Horizontal overflow at {w}x{h}: docW={batch_res['docW']} > winW={batch_res['winW']}")
        if batch_res["exceedsMaxWidth"]:
            failures.append(f"Quote width {batch_res['quoteW']}px exceeds maximum at {w}x{h}")
        if batch_res["exceedsViewportSafe"]:
            failures.append(f"Quote width {batch_res['quoteW']}px exceeds viewport safe boundary at {w}x{h}")

        # Check line-height closures to baseline multiples (24px or 12px)
        if w >= 1440:
            if abs(batch_res["textLh"] - 48.0) > 1.0:
                failures.append(f"At {w}x{h}: widescreen quote-text line-height {batch_res['textLh']}px != 48px (2.0 * L_base)")
            if abs(batch_res["textMb"] - 24.0) > 1.0:
                failures.append(f"At {w}x{h}: widescreen quote-text margin-bottom {batch_res['textMb']}px != 24px (1.0 * L_base)")
        elif w >= 768:
            if abs(batch_res["textLh"] - 36.0) > 1.0:
                failures.append(f"At {w}x{h}: desktop quote-text line-height {batch_res['textLh']}px != 36px (1.5 * L_base)")
            if abs(batch_res["textMb"] - 12.0) > 1.0:
                failures.append(f"At {w}x{h}: desktop quote-text margin-bottom {batch_res['textMb']}px != 12px (0.5 * L_base)")

        if abs(batch_res["authorLh"] - 24.0) > 1.0:
            failures.append(f"At {w}x{h}: quote-author line-height {batch_res['authorLh']}px != 24px (1.0 * L_base)")

    return {
        "passed": len(failures) == 0,
        "results": results,
        "failures_count": len(failures),
        "failures": failures
    }


# ==============================================================================
# Challenge 4: Elevation Hierarchy & Spatial Separation
# ==============================================================================
def challenge_elevation_hierarchy_and_separation(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test vertical elevation ladder:
    - Mode Switcher: bottom: 24px (1 * L_base), z-index: 30
    - Scratch HUD: bottom: 96px (4 * L_base), z-index: 20
    - Interactive Hint: bottom: 96px (4 * L_base), z-index: 20
    - Mode Toast: bottom: 144px (6 * L_base), z-index: 80
    Examines vertical stacking order, monotonicity, z-index segregation, and bounding boxes.
    """
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    res = page.evaluate("""() => {
        const switcher = document.getElementById('mode-switcher');
        const scratchHud = document.getElementById('scratch-hud');
        const interactiveHint = document.getElementById('interactive-hint');
        const modeToast = document.getElementById('mode-toast');

        const sCs = window.getComputedStyle(switcher);
        const hudCs = window.getComputedStyle(scratchHud);
        const toastCs = window.getComputedStyle(modeToast);

        const sBottom = parseFloat(sCs.bottom);
        const hudBottom = parseFloat(hudCs.bottom);
        const toastBottom = parseFloat(toastCs.bottom);

        const sZ = parseInt(sCs.zIndex, 10);
        const hudZ = parseInt(hudCs.zIndex, 10);
        const toastZ = parseInt(toastCs.zIndex, 10);

        // Click scratch mode button
        const mswScratchBtn = document.getElementById('msw-scratch-btn');
        if (mswScratchBtn) mswScratchBtn.click();

        // Trigger toast
        if (window.__gardenEngine && typeof window.__gardenEngine.showToast === 'function') {
            window.__gardenEngine.showToast('Test Toast Notification');
        }

        const sRect = switcher.getBoundingClientRect();
        const hudRect = scratchHud.getBoundingClientRect();
        const toastRect = modeToast.getBoundingClientRect();

        const switcherHudOverlap = !(sRect.top >= hudRect.bottom || sRect.bottom <= hudRect.top);
        const hudToastOverlap = !(hudRect.top >= toastRect.bottom || hudRect.bottom <= toastRect.top);

        const verticalOverlapPx = hudToastOverlap ? Math.max(0, hudRect.bottom - toastRect.top, toastRect.bottom - hudRect.top) : 0;

        return {
            sBottom,
            hudBottom,
            toastBottom,
            sZ,
            hudZ,
            toastZ,
            sRect: { top: sRect.top, bottom: sRect.bottom, height: sRect.height },
            hudRect: { top: hudRect.top, bottom: hudRect.bottom, height: hudRect.height },
            toastRect: { top: toastRect.top, bottom: toastRect.bottom, height: toastRect.height },
            switcherHudOverlap,
            hudToastOverlap,
            verticalOverlapPx,
            elevationMonotonic: (sBottom < hudBottom) && (hudBottom < toastBottom)
        };
    }""")

    failures = []
    findings = []

    if not res["elevationMonotonic"]:
        failures.append(f"Elevation bottom offsets not strictly monotonic: Switcher={res['sBottom']}px, HUD={res['hudBottom']}px, Toast={res['toastBottom']}px")
    if abs(res["sBottom"] - 24.0) > 1.0:
        failures.append(f"Switcher bottom {res['sBottom']}px != 24px (1 * L_base)")
    if abs(res["hudBottom"] - 96.0) > 1.0:
        failures.append(f"Scratch HUD bottom {res['hudBottom']}px != 96px (4 * L_base)")
    if abs(res["toastBottom"] - 144.0) > 1.0:
        failures.append(f"Mode Toast bottom {res['toastBottom']}px != 144px (6 * L_base)")
    if res["switcherHudOverlap"]:
        failures.append("Vertical collision detected between Mode Switcher and Scratch HUD")

    # Adversarial note on Toast vs Scratch HUD overlap
    if res["hudToastOverlap"]:
        findings.append({
            "dimension": "Capsule Vertical Overlap",
            "detail": f"Scratch HUD top ({res['hudRect']['top']:.1f}px) reaches above Toast bottom ({res['toastRect']['bottom']:.1f}px) during simultaneous presentation by {res['verticalOverlapPx']:.1f}px. Z-index segregation (Toast z={res['toastZ']} > HUD z={res['hudZ']}) prevents occluding interaction, but geometric capsule overlap is present."
        })

    return {
        "passed": len(failures) == 0,
        "metrics": res,
        "findings": findings,
        "failures_count": len(failures),
        "failures": failures
    }


# ==============================================================================
# Challenge 5: Brush Control Panel, Draggable Coordinates & Loupe Safety
# ==============================================================================
def challenge_brush_panel_invariants(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test Artisan Brush Panel & Popup:
    - Default position: top 24px, right 24px
    - Custom draggable position override: .is-custom-position overrides right/bottom
    - Closed popup opacity: 0 and pointer-events: none (zero interference with loupe / hitPanel)
    - Open popup elevation: raising z-index to --z-modal (70)
    """
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    res = page.evaluate("""() => {
        const panel = document.getElementById('brush-control');
        const popup = document.getElementById('brush-popup');
        const btn = document.getElementById('brush-toggle-btn');

        const initialCs = window.getComputedStyle(panel);
        const initialTop = parseFloat(initialCs.top);
        const initialRight = parseFloat(initialCs.right);
        const initialZ = parseInt(initialCs.zIndex, 10);

        // Verify closed popup properties
        const popupClosedCs = window.getComputedStyle(popup);
        const closedOpacity = parseFloat(popupClosedCs.opacity);
        const closedPointerEvents = popupClosedCs.pointerEvents;

        // Test custom position override simulation
        panel.classList.add('is-custom-position');
        panel.style.left = '250px';
        panel.style.top = '350px';
        const customRect = panel.getBoundingClientRect();
        const customLeft = customRect.left;
        const customTop = customRect.top;

        // Reset custom position
        panel.classList.remove('is-custom-position');
        panel.style.left = '';
        panel.style.top = '';

        // Open popup and inspect z-index
        btn.click();
        const popupOpenCs = window.getComputedStyle(popup);
        const panelOpenCs = window.getComputedStyle(panel);
        const openOpacity = parseFloat(popupOpenCs.opacity);
        const openPanelZ = parseInt(panelOpenCs.zIndex, 10);

        // Close popup again
        btn.click();

        return {
            initialTop,
            initialRight,
            initialZ,
            closedOpacity,
            closedPointerEvents,
            customLeft,
            customTop,
            openOpacity,
            openPanelZ
        };
    }""")

    failures = []
    if abs(res["initialTop"] - 24.0) > 1.0:
        failures.append(f"Brush panel initial top {res['initialTop']}px != 24px")
    if abs(res["initialRight"] - 24.0) > 1.0:
        failures.append(f"Brush panel initial right {res['initialRight']}px != 24px")
    if res["closedOpacity"] != 0:
        failures.append(f"Closed brush popup opacity {res['closedOpacity']} != 0")
    if res["closedPointerEvents"] != "none":
        failures.append(f"Closed brush popup pointer-events '{res['closedPointerEvents']}' != 'none'")
    if abs(res["customLeft"] - 250.0) > 1.0 or abs(res["customTop"] - 350.0) > 1.0:
        failures.append(f"Custom draggable position was not respected: left={res['customLeft']} (exp 250), top={res['customTop']} (exp 350)")
    if res["openPanelZ"] < 70:
        failures.append(f"Open brush panel z-index {res['openPanelZ']} is not elevated to modal tier (>= 70)")

    return {
        "passed": len(failures) == 0,
        "metrics": res,
        "failures_count": len(failures),
        "failures": failures
    }


# ==============================================================================
# Main Runner
# ==============================================================================
def main():
    print("=" * 80)
    print(" 🔬 ADVERSARIAL STRESS HARNESS — Milestone 2 Floating Controls & Alignment")
    print(" Agent: m2_challenger_1 (EMPIRICAL CHALLENGER)")
    print("=" * 80)

    server = LocalServer()
    server.start()
    base_url = server.base_url

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            page = browser.new_page()

            # Challenge 1
            print("\n[1/5] Running Challenge 1: Bottom Baseline Alignment Rigor (0.00px diff)...")
            c1 = challenge_baseline_alignment(page, base_url)
            print(f"      Passed: {c1['passed']} (Tested {c1['total_viewports']} viewports, Failures: {c1['failures_count']})")
            for r in c1['results']:
                print(f"      - {r['viewport']}: Switcher={r['switcher_bottom']:.2f}px, Help={r['help_bottom']:.2f}px, Diff={r['diff']:.3f}px [Exact 0.00px: {r['is_exact_zero']}]")
            if not c1['passed']:
                for f in c1['failures']:
                    print(f"      [FAIL] {f}")

            # Challenge 2
            print("\n[2/5] Running Challenge 2: Optical Center Ratio (Y_center / H in [0.440, 0.460])...")
            c2 = challenge_optical_center_ratio(page, base_url)
            print(f"      Passed: {c2['passed']} (Tested {c2['viewports_evaluated']} viewports, Quote stress items: {len(c2['quote_stress_results'])}, Failures: {c2['failures_count']})")
            for vr in c2['viewport_results']:
                print(f"      - {vr['viewport']}: centerY={vr['centerY']:.1f}px / {vr['winH']}px -> Ratio={vr['ratio']:.4f} [Valid in [0.44, 0.46]: {vr['valid']}]")
            print("      Quote Text Stress Variations:")
            for qr in c2['quote_stress_results']:
                print(f"      - {qr['desc']}: size={qr['width']:.0f}x{qr['height']:.0f}px -> Ratio={qr['ratio']:.4f} [Valid: {qr['valid']}]")
            if not c2['passed']:
                for f in c2['failures']:
                    print(f"      [FAIL] {f}")

            # Challenge 3
            print("\n[3/5] Running Challenge 3: Reading Measure Bounds & Typography Closures...")
            c3 = challenge_reading_measure_and_typography(page, base_url)
            print(f"      Passed: {c3['passed']} (Failures: {c3['failures_count']})")
            for res in c3['results']:
                print(f"      - {res['viewport']}: width={res['quoteW']:.1f}px (<=768px: {not res['exceedsMaxWidth']}), textLh={res['textLh']}px, authorLh={res['authorLh']}px, overflow={res['hasOverflow']}")
            if not c3['passed']:
                for f in c3['failures']:
                    print(f"      [FAIL] {f}")

            # Challenge 4
            print("\n[4/5] Running Challenge 4: Elevation Hierarchy & Capsule Separation...")
            c4 = challenge_elevation_hierarchy_and_separation(page, base_url)
            print(f"      Passed: {c4['passed']} (Failures: {c4['failures_count']})")
            m = c4['metrics']
            print(f"      - Ladder: Switcher={m['sBottom']}px (z={m['sZ']}), HUD={m['hudBottom']}px (z={m['hudZ']}), Toast={m['toastBottom']}px (z={m['toastZ']})")
            print(f"      - Monotonic Bottom: {m['elevationMonotonic']}, Switcher-HUD Overlap: {m['switcherHudOverlap']}, HUD-Toast Geometric Overlap: {m['hudToastOverlap']}")
            for finding in c4['findings']:
                print(f"      - [ADVERSARIAL NOTE] {finding['dimension']}: {finding['detail']}")
            if not c4['passed']:
                for f in c4['failures']:
                    print(f"      [FAIL] {f}")

            # Challenge 5
            print("\n[5/5] Running Challenge 5: Brush Control Panel, Custom Drag & Loupe Safety...")
            c5 = challenge_brush_panel_invariants(page, base_url)
            print(f"      Passed: {c5['passed']} (Failures: {c5['failures_count']})")
            bm = c5['metrics']
            print(f"      - Default: top={bm['initialTop']}px, right={bm['initialRight']}px, z={bm['initialZ']}")
            print(f"      - Closed popup: opacity={bm['closedOpacity']}, pointer-events={bm['closedPointerEvents']}")
            print(f"      - Draggable custom coords: left={bm['customLeft']}px, top={bm['customTop']}px")
            print(f"      - Open popup elevated z: {bm['openPanelZ']}")
            if not c5['passed']:
                for f in c5['failures']:
                    print(f"      [FAIL] {f}")

            browser.close()

            all_passed = c1['passed'] and c2['passed'] and c3['passed'] and c4['passed'] and c5['passed']
            print("\n" + "=" * 80)
            if all_passed:
                print(" 🏆 FINAL CHALLENGE RESULT: ALL ADVERSARIAL STRESS TESTS PASSED (100%)")
            else:
                print(" ❌ FINAL CHALLENGE RESULT: ADVERSARIAL FAILURES DETECTED")
            print("=" * 80)

            return 0 if all_passed else 1

    finally:
        server.stop()


if __name__ == "__main__":
    sys.exit(main())

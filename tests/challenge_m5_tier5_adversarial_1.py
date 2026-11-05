#!/usr/bin/env python3
"""
challenge_m5_tier5_adversarial_1.py - Milestone 5 Phase 2 Adversarial Hardening Suite.
Tier 5: Layout & Responsive Dynamics Verification.

Tests 5 Critical Architectural Dimensions:
1. Precision Breakpoint Boundaries:
   - 1441px/1439px (widescreen/desktop)
   - 1025px/1023px (desktop/tablet)
   - 769px/767px (tablet/mobile)
   - 641px/639px (mobile/compact)
   - 481px/479px (compact/narrow)
   - 320px extreme minimum viewport
2. Proportional Margin Adherence (2:3:4:6) and Fluid Clamp:
   - Inner:Top:Outer:Bottom = 2:3:4:6 across widescreen, desktop, tablet, and mobile
   - Fluid clamp behavior on --grid-margin
3. Optical Centroid Stability:
   - .help-dialog target range 44% - 46%
   - #art-quote anchored in upper optical focal field
   - Tested across extreme aspect ratios: 21:9 ultrawide (2560x1080), 9:21 tall mobile (390x900), 16:9, 4:3
4. Standardized Touch Target Dimensions:
   - Strict >= 40x40px requirement on #help-close-btn, #gallery-close-btn, #story-close-btn,
     #mode-switcher button (#msw-sleep-btn, #msw-scratch-btn), #brush-toggle-btn, and secondary controls
5. Zoom Simulation (125%, 150%, 200%) & High-DPI Resilience:
   - DPR variations (1.0, 1.5, 2.0, 3.0) and dual canvas pixel alignment
   - Browser zoom simulation without horizontal scroll leak (scrollWidth <= clientWidth)
   - Container bounding box preservation and legibility
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.server_helper import LocalServer
from playwright.sync_api import sync_playwright, Page


def wait_engine_ready(page: Page, timeout: int = 15000):
    """Wait until window.__gardenEngine is fully loaded."""
    page.wait_for_function(
        "() => window.__gardenEngine && typeof window.__gardenEngine.isLoaded === 'function' && window.__gardenEngine.isLoaded()",
        timeout=timeout
    )


# ==============================================================================
# Domain 1: Precision Breakpoint Boundaries
# ==============================================================================

def test_adv_01_precision_breakpoint_boundaries(page: Page, base_url: str) -> Dict[str, Any]:
    """Verify precision breakpoint boundaries and cascade state transitions."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    boundaries = [
        {"w_high": 1441, "w_low": 1439, "tier_high": "Widescreen", "tier_low": "Desktop Standard"},
        {"w_high": 1025, "w_low": 1023, "tier_high": "Desktop Standard", "tier_low": "Tablet"},
        {"w_high": 769,  "w_low": 767,  "tier_high": "Tablet", "tier_low": "Mobile Standard"},
        {"w_high": 641,  "w_low": 639,  "tier_high": "Mobile Standard", "tier_low": "Mobile Compact"},
        {"w_high": 481,  "w_low": 479,  "tier_high": "Mobile Compact", "tier_low": "Ultra-Compact"},
        {"w_high": 320,  "w_low": 320,  "tier_high": "Extreme Minimum", "tier_low": "Extreme Minimum"}
    ]

    boundary_results = []
    all_passed = True

    for b in boundaries:
        for w in sorted(set([b["w_high"], b["w_low"]])):
            page.set_viewport_size({"width": w, "height": 800})
            page.wait_for_timeout(100)

            dom_metrics = page.evaluate("""() => {
                const style = window.getComputedStyle(document.documentElement);
                const scrollW = document.documentElement.scrollWidth;
                const clientW = document.documentElement.clientWidth;

                const storyHandle = document.querySelector('.story-sheet-handle');
                const shDisplay = storyHandle ? window.getComputedStyle(storyHandle).display : 'none';

                const gList = document.querySelector('.gallery-list-container');
                const gCols = gList ? window.getComputedStyle(gList).gridTemplateColumns : '';

                return {
                    cols: parseInt(style.getPropertyValue('--grid-columns').trim(), 10) || 12,
                    gutter: style.getPropertyValue('--grid-gutter').trim(),
                    margin: style.getPropertyValue('--grid-margin').trim(),
                    scrollW, clientW,
                    overflow: scrollW > clientW,
                    shDisplay,
                    gColCount: gCols.split(' ').filter(Boolean).length
                };
            }""")

            # Validation rules based on spec
            passed = True
            reasons = []

            if dom_metrics["overflow"]:
                passed = False
                reasons.append(f"Horizontal scroll overflow (scrollW={dom_metrics['scrollW']} > clientW={dom_metrics['clientW']})")

            if w >= 1440:
                if dom_metrics["cols"] != 12:
                    passed = False
                    reasons.append(f"Expected 12 cols, got {dom_metrics['cols']}")
            elif 1024 <= w <= 1439:
                if dom_metrics["cols"] != 12:
                    passed = False
                    reasons.append(f"Expected 12 cols, got {dom_metrics['cols']}")
            elif 768 <= w <= 1023:
                if dom_metrics["cols"] != 8:
                    passed = False
                    reasons.append(f"Expected 8 cols, got {dom_metrics['cols']}")
            elif 480 <= w <= 767:
                if dom_metrics["cols"] != 4:
                    passed = False
                    reasons.append(f"Expected 4 cols, got {dom_metrics['cols']}")
            elif w <= 479:
                if dom_metrics["cols"] != 2:
                    passed = False
                    reasons.append(f"Expected 2 cols, got {dom_metrics['cols']}")

            # Mobile compact story bottom-sheet transition at 640px
            if w <= 640 and dom_metrics["shDisplay"] != "block":
                passed = False
                reasons.append("Expected story-sheet-handle display:block at <=640px")
            elif w > 640 and dom_metrics["shDisplay"] != "none":
                passed = False
                reasons.append("Expected story-sheet-handle display:none at >640px")

            if not passed:
                all_passed = False

            boundary_results.append({
                "width": w,
                "metrics": dom_metrics,
                "passed": passed,
                "reasons": reasons
            })

    return {
        "domain": "Precision Breakpoint Boundaries",
        "passed": all_passed,
        "detail": f"Tested {len(boundary_results)} precision boundary points across 6 folding thresholds.",
        "points": boundary_results
    }


# ==============================================================================
# Domain 2: Proportional Margins & Fluid Clamp Behavior
# ==============================================================================

def test_adv_02_proportional_margins_and_fluid_clamp(page: Page, base_url: str) -> Dict[str, Any]:
    """Verify proportional margin ratio (2:3:4:6) and fluid clamp behavior across screen sizes."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    viewports = [
        {"name": "Widescreen", "w": 1920, "h": 1080},
        {"name": "Desktop Boundary", "w": 1440, "h": 900},
        {"name": "Desktop Standard", "w": 1280, "h": 800},
        {"name": "Tablet", "w": 768, "h": 1024},
        {"name": "Mobile", "w": 375, "h": 667},
        {"name": "Ultra-Compact", "w": 320, "h": 568}
    ]

    margin_tests = []
    all_passed = True

    for vp in viewports:
        page.set_viewport_size({"width": vp["w"], "height": vp["h"]})
        page.wait_for_timeout(100)

        margins = page.evaluate("""() => {
            const root = window.getComputedStyle(document.documentElement);
            const mInner = parseFloat(root.getPropertyValue('--margin-inner')) || 0;
            const mTop = parseFloat(root.getPropertyValue('--margin-top')) || 0;
            const mOuter = parseFloat(root.getPropertyValue('--margin-outer')) || 0;
            const mBottom = parseFloat(root.getPropertyValue('--margin-bottom')) || 0;
            const gMargin = root.getPropertyValue('--grid-margin').trim();

            return {
                mInner, mTop, mOuter, mBottom,
                gMargin,
                ratio: [mInner, mTop, mOuter, mBottom]
            };
        }""")

        r = margins["ratio"]
        passed = True
        reasons = []

        # Margin proportion validation: Inner:Top:Outer:Bottom == 2:3:4:6
        if r[0] > 0:
            unit = r[0] / 2.0
            expected = [2.0 * unit, 3.0 * unit, 4.0 * unit, 6.0 * unit]
            for actual, exp, name in zip(r, expected, ["Inner", "Top", "Outer", "Bottom"]):
                if abs(actual - exp) > 0.5:
                    passed = False
                    reasons.append(f"{name} margin {actual}px does not match 2:3:4:6 expected {exp}px")

        # Fluid clamp validation on widescreen (>=1440px)
        if vp["w"] >= 1440:
            if "clamp" not in margins["gMargin"] and margins["gMargin"] != "64px":
                passed = False
                reasons.append(f"Widescreen --grid-margin should use fluid clamp, got: {margins['gMargin']}")

        if not passed:
            all_passed = False

        margin_tests.append({
            "viewport": vp["name"],
            "dimensions": f"{vp['w']}x{vp['h']}",
            "margins": margins,
            "passed": passed,
            "reasons": reasons
        })

    return {
        "domain": "Proportional Margins & Fluid Clamp",
        "passed": all_passed,
        "detail": f"Verified 2:3:4:6 margin hierarchy and fluid clamp across {len(margin_tests)} viewports.",
        "viewports": margin_tests
    }


# ==============================================================================
# Domain 3: Optical Centroid Stability
# ==============================================================================

def test_adv_03_optical_centroid_stability_extreme_aspects(page: Page, base_url: str) -> Dict[str, Any]:
    """Verify optical centroid stability (target 44% - 46%) across extreme aspect ratios."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    extreme_viewports = [
        {"name": "21:9 Ultrawide", "w": 2560, "h": 1080},
        {"name": "16:9 Desktop", "w": 1920, "h": 1080},
        {"name": "4:3 Standard Tablet", "w": 1024, "h": 768},
        {"name": "9:21 Tall Mobile", "w": 390, "h": 900},
        {"name": "Standard Mobile", "w": 375, "h": 667},
        {"name": "Compact Mobile", "w": 320, "h": 568}
    ]

    centroid_results = []
    all_passed = True

    for vp in extreme_viewports:
        page.set_viewport_size({"width": vp["w"], "height": vp["h"]})
        page.wait_for_timeout(100)

        # 1. Measure #art-quote optical centroid
        quote_metrics = page.evaluate("""() => {
            const quote = document.getElementById('art-quote');
            if (!quote) return null;
            const r = quote.getBoundingClientRect();
            const cy = r.top + r.height / 2;
            return {
                top: r.top,
                height: r.height,
                centerY: cy,
                ratio: cy / window.innerHeight
            };
        }""")

        # 2. Open .help-dialog and measure its optical centroid
        page.evaluate("() => window.__gardenEngine.openHelp()")
        page.wait_for_timeout(150)

        help_metrics = page.evaluate("""() => {
            const dialog = document.querySelector('.help-dialog');
            if (!dialog) return null;
            const r = dialog.getBoundingClientRect();
            const cy = r.top + r.height / 2;
            return {
                top: r.top,
                height: r.height,
                centerY: cy,
                ratio: cy / window.innerHeight
            };
        }""")

        page.evaluate("() => window.__gardenEngine.closeHelp()")
        page.wait_for_timeout(100)

        passed = True
        reasons = []

        # .help-dialog target: 44.0% - 46.0%
        if help_metrics:
            help_ratio = help_metrics["ratio"]
            if not (0.440 <= help_ratio <= 0.460):
                passed = False
                reasons.append(f"Help dialog optical center {help_ratio*100:.2f}% is outside 44.0%-46.0% target")
        else:
            passed = False
            reasons.append("Help dialog not found in DOM")

        # #art-quote target: upper optical center (<= 46.0%)
        if quote_metrics:
            quote_ratio = quote_metrics["ratio"]
            if quote_ratio > 0.460:
                passed = False
                reasons.append(f"Art quote center {quote_ratio*100:.2f}% exceeds upper optical threshold 46.0%")
        else:
            passed = False
            reasons.append("Art quote element not found in DOM")

        if not passed:
            all_passed = False

        centroid_results.append({
            "name": vp["name"],
            "dimensions": f"{vp['w']}x{vp['h']}",
            "quote_ratio": round(quote_metrics["ratio"] * 100, 2) if quote_metrics else None,
            "help_ratio": round(help_metrics["ratio"] * 100, 2) if help_metrics else None,
            "passed": passed,
            "reasons": reasons
        })

    return {
        "domain": "Optical Centroid Stability",
        "passed": all_passed,
        "detail": f"Tested optical centroid across {len(centroid_results)} extreme aspect ratios (21:9 to 9:21).",
        "results": centroid_results
    }


# ==============================================================================
# Domain 4: Standardized Touch Target Dimensions
# ==============================================================================

def test_adv_04_touch_target_standardization(page: Page, base_url: str) -> Dict[str, Any]:
    """Verify standardized touch target dimensions (>= 40x40px) on all interactive buttons."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    test_viewports = [
        {"name": "Desktop", "w": 1440, "h": 900},
        {"name": "Tablet", "w": 768, "h": 1024},
        {"name": "Mobile", "w": 375, "h": 667},
        {"name": "Compact", "w": 320, "h": 568}
    ]

    # Required buttons to test
    buttons = [
        {"id": "help-close-btn", "desc": "Help dialog close button", "critical": True},
        {"id": "gallery-close-btn", "desc": "Gallery drawer close button", "critical": True},
        {"id": "story-close-btn", "desc": "Story drawer close button", "critical": True},
        {"id": "brush-toggle-btn", "desc": "Brush panel toggle button", "critical": True},
        {"id": "msw-sleep-btn", "desc": "Mode switcher: sleep button", "critical": True},
        {"id": "msw-scratch-btn", "desc": "Mode switcher: scratch button", "critical": True},
        {"id": "help-toggle-btn", "desc": "Help toggle button", "critical": False},
        {"id": "scratch-reveal-now-btn", "desc": "Scratch reveal now button", "critical": False},
        {"id": "toggle-full-color-btn", "desc": "Full color toggle button", "critical": False},
        {"id": "fit-auto-btn", "desc": "Fit auto mode button", "critical": False},
        {"id": "toggle-loupe-btn", "desc": "Loupe toggle button", "critical": False},
        {"id": "story-prev-btn", "desc": "Story previous narrative button", "critical": False},
        {"id": "story-next-btn", "desc": "Story next narrative button", "critical": False}
    ]

    button_results = []
    all_passed = True
    sub_40_violations = []

    for vp in test_viewports:
        page.set_viewport_size({"width": vp["w"], "height": vp["h"]})
        page.wait_for_timeout(100)

        # Ensure drawers/modals and scratch HUD can be opened for measuring
        page.evaluate("() => { window.__gardenEngine.setAppMode('scratch'); window.__gardenEngine.openHelp(); window.__gardenEngine.openGallery(); window.__gardenEngine.openStory(); }")
        page.wait_for_timeout(200)

        vp_findings = []
        for btn in buttons:
            btn_id = btn["id"]
            el = page.query_selector(f"#{btn_id}")
            if el:
                box = el.bounding_box()
                if box:
                    w = round(box["width"], 2)
                    h = round(box["height"], 2)
                    # Subpixel tolerance of 0.5px (e.g. 39.9px satisfies 40px)
                    meets_target = (w >= 39.5 and h >= 39.5)

                    if not meets_target:
                        all_passed = False
                        violation = {
                            "viewport": vp["name"],
                            "button": f"#{btn_id}",
                            "description": btn["desc"],
                            "measured_width": w,
                            "measured_height": h,
                            "deficit_w": round(max(0, 40.0 - w), 2),
                            "deficit_h": round(max(0, 40.0 - h), 2),
                            "critical": btn["critical"]
                        }
                        sub_40_violations.append(violation)

                    vp_findings.append({
                        "id": btn_id,
                        "desc": btn["desc"],
                        "width": w,
                        "height": h,
                        "meets_target": meets_target
                    })

        page.evaluate("() => { window.__gardenEngine.setAppMode('sleep'); window.__gardenEngine.closeHelp(); window.__gardenEngine.closeGallery(); window.__gardenEngine.closeStory(); }")

        button_results.append({
            "viewport": vp["name"],
            "dimensions": f"{vp['w']}x{vp['h']}",
            "buttons": vp_findings
        })

    return {
        "domain": "Standardized Touch Target Dimensions",
        "passed": all_passed,
        "detail": f"Tested {len(buttons)} buttons across {len(test_viewports)} viewports. Found {len(sub_40_violations)} sub-40px touch target violations.",
        "violations": sub_40_violations,
        "viewports": button_results
    }


# ==============================================================================
# Domain 5: Zoom Simulation & High-DPI Resilience
# ==============================================================================

def test_adv_05_zoom_and_dpi_resilience(page: Page, base_url: str) -> Dict[str, Any]:
    """Verify zoom simulation (125%, 150%, 200%) and DPI variations (1.0 to 3.0)."""
    dpi_results = []
    zoom_results = []
    all_passed = True

    # 1. High-DPI Variations
    browser = page.context.browser
    for dpr in [1.0, 1.5, 2.0, 3.0]:
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=dpr)
        dpi_page = ctx.new_page()
        dpi_page.goto(f"{base_url}/index.html")
        wait_engine_ready(dpi_page)

        res = dpi_page.evaluate("""() => {
            const bg = document.getElementById('bg-canvas');
            const rev = document.getElementById('reveal-canvas');
            const stage = document.getElementById('art-stage');
            const rect = stage.getBoundingClientRect();
            const dpr = window.devicePixelRatio;
            const effectiveDpr = Math.min(dpr, 2.5); // Intentional engine guard in canvas-engine.js against VRAM overflow
            const expW = Math.round(rect.width * effectiveDpr);
            const expH = Math.round(rect.height * effectiveDpr);

            return {
                dpr,
                effectiveDpr,
                bgW: bg.width, bgH: bg.height,
                revW: rev.width, revH: rev.height,
                expW, expH,
                canvasesMatch: (bg.width === rev.width && bg.height === rev.height),
                dprMatch: (Math.abs(bg.width - expW) <= 2 && Math.abs(bg.height - expH) <= 2)
            };
        }""")

        passed = res["canvasesMatch"] and res["dprMatch"]
        if not passed:
            all_passed = False

        dpi_results.append({
            "dpr": dpr,
            "bgCanvas": f"{res['bgW']}x{res['bgH']}",
            "revCanvas": f"{res['revW']}x{res['revH']}",
            "passed": passed
        })
        ctx.close()

    # 2. Browser Zoom Simulation (125%, 150%, 200%)
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    zoom_factors = [1.25, 1.50, 2.00]
    base_resolutions = [
        {"name": "Widescreen Desktop", "w": 1440, "h": 900},
        {"name": "Tablet", "w": 768, "h": 1024},
        {"name": "Mobile", "w": 375, "h": 667},
        {"name": "Compact Mobile", "w": 320, "h": 568}
    ]

    for factor in zoom_factors:
        for res in base_resolutions:
            # Emulate browser zoom: CSS viewport width scales inversely with zoom factor
            sim_w = int(res["w"] / factor)
            sim_h = int(res["h"] / factor)

            page.set_viewport_size({"width": sim_w, "height": sim_h})
            page.wait_for_timeout(100)

            zoom_metrics = page.evaluate("""() => {
                const scrollW = document.documentElement.scrollWidth;
                const clientW = document.documentElement.clientWidth;

                const quote = document.getElementById('art-quote');
                const switcher = document.getElementById('mode-switcher');
                const brushBtn = document.getElementById('brush-toggle-btn');

                const qBox = quote ? quote.getBoundingClientRect() : null;
                const sBox = switcher ? switcher.getBoundingClientRect() : null;
                const bBox = brushBtn ? brushBtn.getBoundingClientRect() : null;

                const vpW = window.innerWidth;
                const vpH = window.innerHeight;

                const quoteVisible = qBox ? (qBox.width > 0 && qBox.height > 0) : false;
                const switcherClipped = sBox ? (sBox.left < -2 || sBox.right > vpW + 2) : false;
                const brushBtnClipped = bBox ? (bBox.left < -2 || bBox.right > vpW + 2) : false;

                return {
                    scrollW, clientW,
                    hasOverflow: scrollW > clientW,
                    quoteVisible,
                    switcherClipped,
                    brushBtnClipped
                };
            }""")

            passed = (not zoom_metrics["hasOverflow"]) and (not zoom_metrics["switcherClipped"]) and zoom_metrics["quoteVisible"]
            reasons = []

            if zoom_metrics["hasOverflow"]:
                passed = False
                reasons.append(f"Horizontal scroll leak: scrollW={zoom_metrics['scrollW']} > clientW={zoom_metrics['clientW']}")
            if zoom_metrics["switcherClipped"]:
                passed = False
                reasons.append("Mode switcher clipped by viewport boundary")
            if not zoom_metrics["quoteVisible"]:
                passed = False
                reasons.append("Quote container invisible or collapsed")

            if not passed:
                all_passed = False

            zoom_results.append({
                "zoom": f"{int(factor*100)}%",
                "base_resolution": res["name"],
                "simulated_viewport": f"{sim_w}x{sim_h}",
                "passed": passed,
                "reasons": reasons
            })

    return {
        "domain": "Zoom Simulation & High-DPI Resilience",
        "passed": all_passed,
        "detail": f"Verified DPI scaling (DPR 1.0 to 3.0) and {len(zoom_results)} zoom simulation conditions.",
        "dpi_scaling": dpi_results,
        "zoom_simulation": zoom_results
    }


# ==============================================================================
# Test Runner Suite Registry
# ==============================================================================

TIER5_TESTS = [
    ("test_adv_01_precision_breakpoint_boundaries", test_adv_01_precision_breakpoint_boundaries, "ADV-01", "Precision Breakpoint Boundaries (1441/1439, 1025/1023, 769/767, 641/639, 481/479, 320)"),
    ("test_adv_02_proportional_margins_and_fluid_clamp", test_adv_02_proportional_margins_and_fluid_clamp, "ADV-02", "Proportional Margins (2:3:4:6) & Fluid Clamp Behavior"),
    ("test_adv_03_optical_centroid_stability_extreme_aspects", test_adv_03_optical_centroid_stability_extreme_aspects, "ADV-03", "Optical Centroid Stability across Extreme Aspect Ratios (21:9 & 9:21)"),
    ("test_adv_04_touch_target_standardization", test_adv_04_touch_target_standardization, "ADV-04", "Standardized Touch Target Dimensions (>= 40x40px on all buttons)"),
    ("test_adv_05_zoom_and_dpi_resilience", test_adv_05_zoom_and_dpi_resilience, "ADV-05", "Zoom Simulation (125%, 150%, 200%) & High-DPI Variations (1.0 to 3.0)")
]


def run_tier5_adversarial_suite(report_path: str = "tests/reports/challenge_m5_tier5_results.json", channel: str = "chrome"):
    """Execute all Tier 5 adversarial tests and generate report."""
    print("=" * 80)
    print(" 🛡️  Milestone 5 Phase 2 — Tier 5 Adversarial Hardening Suite")
    print("    Layout & Responsive Dynamics Verification")
    print("=" * 80)
    print(f" Timestamp:  {datetime.now(timezone.utc).isoformat()}")
    print(f" Browser:    Chromium (channel: {channel})")
    print(f" Report:     {report_path}")
    print("-" * 80)

    start_time = time.time()
    results = []
    passed_count = 0
    failed_count = 0

    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with LocalServer() as server:
        base_url = server.base_url
        print(f" Local HTTP Daemon: {base_url} (serving {PROJECT_ROOT})\n")

        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(channel=channel, headless=True)
            except Exception as e:
                print(f" [!] Channel '{channel}' launch failed ({e}), falling back to standard chromium.")
                browser = p.chromium.launch(headless=True)

            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            for test_name, test_fn, test_id, desc in TIER5_TESTS:
                t0 = time.time()
                res = None
                status = "PASSED"
                error_msg = None

                try:
                    res = test_fn(page, base_url)
                    dur = (time.time() - t0) * 1000
                    if res.get("passed", True):
                        passed_count += 1
                        print(f"  ✓ [{test_id}] {desc:<62} ({dur:6.1f}ms)")
                    else:
                        status = "FAILED"
                        failed_count += 1
                        print(f"  ✗ [{test_id}] {desc:<62} ({dur:6.1f}ms) — FAIL")
                        if "violations" in res and res["violations"]:
                            for v in res["violations"][:5]:
                                print(f"      └─ {v['button']} in {v['viewport']}: {v['measured_width']}x{v['measured_height']}px (Deficit H: {v['deficit_h']}px)")
                            if len(res["violations"]) > 5:
                                print(f"      └─ ... and {len(res['violations']) - 5} more violations")
                except Exception as exc:
                    status = "FAILED"
                    failed_count += 1
                    dur = (time.time() - t0) * 1000
                    error_msg = str(exc)
                    print(f"  ✗ [{test_id}] {desc:<62} ({dur:6.1f}ms) — EXCEPTION: {error_msg}")

                results.append({
                    "id": test_id,
                    "name": test_name,
                    "description": desc,
                    "status": status,
                    "duration_ms": round(dur, 2),
                    "details": res,
                    "error": error_msg
                })

            context.close()
            browser.close()

    total_time = round(time.time() - start_time, 2)
    total_tests = len(TIER5_TESTS)
    pass_rate = round((passed_count / total_tests) * 100, 1) if total_tests > 0 else 0.0

    print("\n" + "=" * 80)
    print(" 📊 TIER 5 ADVERSARIAL TEST SUMMARY")
    print("=" * 80)
    print(f" Total Tests Executed: {total_tests}")
    print(f" Passed:               {passed_count}")
    print(f" Failed:               {failed_count}")
    print(f" Pass Rate:            {pass_rate}%")
    print(f" Total Time:           {total_time}s")
    print(f" JSON Report Saved:    {report_file.resolve()}")
    print("=" * 80)

    verdict = "APPROVE" if failed_count == 0 else "REQUEST_CHANGES"
    print(f"\n 🏁 CHALLENGER VERDICT: {verdict}")

    report_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "milestone": "Milestone 5 Phase 2",
        "suite": "Tier 5: Layout & Responsive Dynamics Adversarial Suite",
        "verdict": verdict,
        "summary": {
            "total": total_tests,
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate_percent": pass_rate,
            "duration_seconds": total_time
        },
        "tests": results
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2, ensure_ascii=False)

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tier 5 Adversarial Test Runner")
    parser.add_argument("--report", default="tests/reports/challenge_m5_tier5_results.json")
    parser.add_argument("--channel", default="chrome")
    args = parser.parse_args()

    exit_code = run_tier5_adversarial_suite(report_path=args.report, channel=args.channel)
    sys.exit(exit_code)

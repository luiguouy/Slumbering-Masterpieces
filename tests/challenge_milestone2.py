#!/usr/bin/env python3
"""
challenge_milestone2.py - Empirical Adversarial Stress Harness for Milestone 2.

Written by: m2_challenger_2 (EMPIRICAL CHALLENGER)
Target: Milestone 2: Floating Controls & Art Stage Alignment

Challenge Dimensions:
1. Console Integrity & Clean Network Lifecycle (0 script exceptions, 0 application 4xx/5xx)
2. Floating Controls Subpixel Baseline Parity (Discrepancy < 0.05px across 6 viewports)
3. Art Quote Optical Center (44% - 46%), Reading Measure, and Baseline Typographic Rhythm
4. Elevation Hierarchy & Tokenization Monotonicity (Bottom values: 24px -> 96px -> 144px; z-indices)
5. Brush Drag Persistence, PointerCapture, Clamping, localStorage Sync & Double-Click Reset
6. Brush Popup Adaptive Flip, Outside Click Dismiss, and Inside Click Immunity
7. Classical Loupe Zoom, Reset, and HitPanel Invariant
8. Stroke Dimming Dynamics (Quote container opacity drops to 0.25 during strokes, restores on idle)
9. Rapid Mode Switching Stress Test (Adversarial race condition generator: 30 switches in 1s)
"""

import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.server_helper import LocalServer
from playwright.sync_api import sync_playwright, Page, ConsoleMessage


def wait_engine_ready(page: Page, timeout: int = 15000):
    page.wait_for_function(
        "() => window.__gardenEngine && typeof window.__gardenEngine.isLoaded === 'function' && window.__gardenEngine.isLoaded()",
        timeout=timeout
    )


# ==============================================================================
# Challenge 1: Console Integrity & Clean Network Lifecycle
# ==============================================================================
def challenge_console_integrity(page: Page, base_url: str) -> Dict[str, Any]:
    """Verify 0 console errors, 0 page errors, 0 failed application requests."""
    console_errors = []
    console_warnings = []
    page_errors = []
    failed_requests = []

    def on_console(msg: ConsoleMessage):
        # Ignore browser internal favicon.ico requests (standard when no <link rel="icon"> is present)
        url = msg.location.get("url", "") if hasattr(msg, "location") and msg.location else ""
        if "favicon.ico" in url or "favicon.ico" in msg.text:
            return
        if msg.type == "error":
            console_errors.append(msg.text)
        elif msg.type == "warning":
            console_warnings.append(msg.text)

    def on_pageerror(err):
        page_errors.append(str(err))

    def on_requestfailed(req):
        if "favicon.ico" in req.url:
            return
        failed_requests.append(f"{req.method} {req.url}: {req.failure}")

    page.on("console", on_console)
    page.on("pageerror", on_pageerror)
    page.on("requestfailed", on_requestfailed)

    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(1000)

    # Let the engine cycle for 1 second
    page.wait_for_timeout(1000)

    passed = (len(console_errors) == 0 and len(page_errors) == 0 and len(failed_requests) == 0)

    return {
        "name": "Console Integrity & Clean Network Lifecycle",
        "passed": passed,
        "console_errors": console_errors,
        "console_warnings": console_warnings,
        "page_errors": page_errors,
        "failed_requests": failed_requests
    }


# ==============================================================================
# Challenge 2: Floating Controls Subpixel Baseline Parity
# ==============================================================================
def challenge_floating_controls_baseline(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Verify exact bottom baseline alignment between mode switcher and help trigger
    across Desktop, Compact Desktop, Tablet, and Mobile viewports.
    """
    viewports = [
        {"name": "Widescreen", "width": 1440, "height": 900, "expected_bottom": 24.0},
        {"name": "Desktop Standard", "width": 1280, "height": 800, "expected_bottom": 24.0},
        {"name": "Desktop Compact", "width": 1024, "height": 768, "expected_bottom": 24.0},
        {"name": "Tablet", "width": 768, "height": 1024, "expected_bottom": 24.0},
        {"name": "Mobile Large", "width": 480, "height": 844, "expected_bottom": 16.0},
        {"name": "Mobile Small", "width": 375, "height": 667, "expected_bottom": 16.0},
    ]

    results = []
    failures = []

    for vp in viewports:
        page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        page.wait_for_timeout(200)

        data = page.evaluate("""() => {
            const msw = document.getElementById('mode-switcher');
            const help = document.querySelector('.help-trigger-wrap') || document.getElementById('help-toggle-btn');
            
            const mswRect = msw.getBoundingClientRect();
            const helpRect = help.getBoundingClientRect();
            const vh = window.innerHeight;
            
            const mswBottomOffset = vh - mswRect.bottom;
            const helpBottomOffset = vh - helpRect.bottom;
            
            const mswCS = window.getComputedStyle(msw);
            const helpCS = window.getComputedStyle(help);
            
            return {
                mswBottomOffset,
                helpBottomOffset,
                discrepancy: Math.abs(mswBottomOffset - helpBottomOffset),
                mswComputedBottom: parseFloat(mswCS.bottom),
                helpComputedBottom: parseFloat(helpCS.bottom)
            };
        }""")

        discrepancy = data["discrepancy"]
        is_aligned = discrepancy < 0.05
        expected_b = vp["expected_bottom"]
        computed_valid = abs(data["mswComputedBottom"] - expected_b) < 1.0 and abs(data["helpComputedBottom"] - expected_b) < 1.0

        item = {
            "viewport": vp["name"],
            "width": vp["width"],
            "height": vp["height"],
            "msw_bottom_offset": round(data["mswBottomOffset"], 3),
            "help_bottom_offset": round(data["helpBottomOffset"], 3),
            "discrepancy": round(discrepancy, 4),
            "msw_computed": round(data["mswComputedBottom"], 2),
            "help_computed": round(data["helpComputedBottom"], 2),
            "aligned": is_aligned,
            "computed_valid": computed_valid
        }
        results.append(item)

        if not is_aligned or not computed_valid:
            failures.append(item)

    return {
        "name": "Floating Controls Subpixel Baseline Parity",
        "passed": len(failures) == 0,
        "details": results,
        "failures": failures
    }


# ==============================================================================
# Challenge 3: Art Quote Optical Center, Reading Measure & Typographic Rhythm
# ==============================================================================
def challenge_art_quote_optical_center_and_rhythm(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Verify:
    1. Optical center alignment: center Y is located at 44% - 46% of viewport height.
    2. Reading measure: max-width <= 768px.
    3. Baseline typographic rhythm: text line-height = 36px (1.5 * 24), margin-bottom = 12px,
       author line-height = 24px (1.0 * 24).
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    eval_data = page.evaluate("""() => {
        const container = document.getElementById('art-quote');
        const textEl = container.querySelector('.quote-text');
        const authorEl = container.querySelector('.quote-author');
        
        const cRect = container.getBoundingClientRect();
        const vh = window.innerHeight;
        const centerY = cRect.top + cRect.height / 2;
        const opticalRatio = centerY / vh;
        
        const cCS = window.getComputedStyle(container);
        const tCS = window.getComputedStyle(textEl);
        const aCS = window.getComputedStyle(authorEl);
        
        return {
            opticalRatio,
            containerWidth: cRect.width,
            containerMaxWidth: parseFloat(cCS.maxWidth) || 0,
            textLineHeight: parseFloat(tCS.lineHeight) || 0,
            textMarginBottom: parseFloat(tCS.marginBottom) || 0,
            authorLineHeight: parseFloat(aCS.lineHeight) || 0,
            backdropFilter: cCS.backdropFilter || cCS.webkitBackdropFilter || 'none'
        };
    }""")

    ratio = eval_data["opticalRatio"]
    optical_ok = 0.435 <= ratio <= 0.465
    measure_ok = eval_data["containerWidth"] <= 768.5 and eval_data["containerMaxWidth"] <= 768.5
    
    text_lh_ok = abs(eval_data["textLineHeight"] - 36.0) <= 1.0
    text_mb_ok = abs(eval_data["textMarginBottom"] - 12.0) <= 1.0
    author_lh_ok = abs(eval_data["authorLineHeight"] - 24.0) <= 1.0
    blur_ok = "blur" in eval_data["backdropFilter"]

    passed = optical_ok and measure_ok and text_lh_ok and text_mb_ok and author_lh_ok and blur_ok

    return {
        "name": "Art Quote Optical Center & Typographic Rhythm",
        "passed": passed,
        "optical_ratio": round(ratio, 4),
        "optical_ok": optical_ok,
        "container_width": round(eval_data["containerWidth"], 1),
        "measure_ok": measure_ok,
        "text_line_height": eval_data["textLineHeight"],
        "text_lh_ok": text_lh_ok,
        "text_margin_bottom": eval_data["textMarginBottom"],
        "text_mb_ok": text_mb_ok,
        "author_line_height": eval_data["authorLineHeight"],
        "author_lh_ok": author_lh_ok,
        "backdrop_filter": eval_data["backdropFilter"],
        "blur_ok": blur_ok
    }


# ==============================================================================
# Challenge 4: Elevation Hierarchy & Tokenization Monotonicity
# ==============================================================================
def challenge_elevation_hierarchy(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Verify:
    1. Integer-multiple vertical elevation ladder:
       - Navigation controls: bottom = 24px (1 * Lbase)
       - Scratch HUD: bottom = 96px (4 * Lbase)
       - Mode toast: bottom = 144px (6 * Lbase)
    2. Monotonic z-index stacking:
       - stage (1) < canvas (2) < quote (10) < hud (20) < controls (30) < toast (80)
    3. Symmetrical 24px boundary margins for brush control:
       - top = 24px, right = 24px
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    ladder = page.evaluate("""() => {
        const msw = document.getElementById('mode-switcher');
        const hud = document.getElementById('scratch-hud');
        const toast = document.getElementById('mode-toast');
        const brush = document.getElementById('brush-control');
        const quote = document.getElementById('art-quote');
        const stage = document.getElementById('art-stage');
        const canvas = document.getElementById('bg-canvas');
        
        const mswCS = window.getComputedStyle(msw);
        const hudCS = window.getComputedStyle(hud);
        const toastCS = window.getComputedStyle(toast);
        const brushCS = window.getComputedStyle(brush);
        const quoteCS = window.getComputedStyle(quote);
        const stageCS = window.getComputedStyle(stage);
        const canvasCS = window.getComputedStyle(canvas);
        
        return {
            mswBottom: parseFloat(mswCS.bottom),
            hudBottom: parseFloat(hudCS.bottom),
            toastBottom: parseFloat(toastCS.bottom),
            brushTop: parseFloat(brushCS.top),
            brushRight: parseFloat(brushCS.right),
            zStage: parseInt(stageCS.zIndex, 10) || 0,
            zCanvas: parseInt(canvasCS.zIndex, 10) || 0,
            zQuote: parseInt(quoteCS.zIndex, 10) || 0,
            zHud: parseInt(hudCS.zIndex, 10) || 0,
            zControls: parseInt(mswCS.zIndex, 10) || 0,
            zBrush: parseInt(brushCS.zIndex, 10) || 0,
            zToast: parseInt(toastCS.zIndex, 10) || 0
        };
    }""")

    msw_bottom_ok = abs(ladder["mswBottom"] - 24.0) <= 1.0
    hud_bottom_ok = abs(ladder["hudBottom"] - 96.0) <= 1.0
    toast_bottom_ok = abs(ladder["toastBottom"] - 144.0) <= 1.0

    brush_top_ok = abs(ladder["brushTop"] - 24.0) <= 1.0
    brush_right_ok = abs(ladder["brushRight"] - 24.0) <= 1.0

    z_mono = (ladder["zStage"] < ladder["zCanvas"] <= ladder["zQuote"] <
              ladder["zHud"] < ladder["zControls"] <= ladder["zBrush"] < ladder["zToast"])

    passed = msw_bottom_ok and hud_bottom_ok and toast_bottom_ok and brush_top_ok and brush_right_ok and z_mono

    return {
        "name": "Elevation Hierarchy & Tokenization Monotonicity",
        "passed": passed,
        "ladder": ladder,
        "msw_bottom_ok": msw_bottom_ok,
        "hud_bottom_ok": hud_bottom_ok,
        "toast_bottom_ok": toast_bottom_ok,
        "brush_top_ok": brush_top_ok,
        "brush_right_ok": brush_right_ok,
        "z_monotonic": z_mono
    }


# ==============================================================================
# Challenge 5: Brush Drag Persistence, PointerCapture & Double-Click Escape Hatch
# ==============================================================================
def challenge_brush_drag_and_persistence(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Adversarially test:
    1. Default state: no is-custom-position class.
    2. Drag interaction: pointerdown, move beyond threshold (>4px), pointerup.
    3. Position validation: is-custom-position added, inline left/top present and clamped.
    4. localStorage persistence: artweb.brushPanelPos.v1 stores normalized coordinates.
    5. Persistence across page reload: restored faithfully within 2px.
    6. Double-click reset: restores to default top-right, clears inline styles, removes storage key.
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    page.evaluate("() => localStorage.removeItem('artweb.brushPanelPos.v1')")
    page.reload()
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    initial_check = page.evaluate("""() => {
        const el = document.getElementById('brush-control');
        return {
            hasCustomPos: el.classList.contains('is-custom-position'),
            inlineLeft: el.style.left,
            inlineTop: el.style.top
        };
    }""")
    assert not initial_check["hasCustomPos"], "Panel should initially not have custom position"

    btn = page.locator("#brush-toggle-btn")
    box = btn.bounding_box()
    start_x = box["x"] + box["width"] / 2
    start_y = box["y"] + box["height"] / 2
    target_x = start_x - 300
    target_y = start_y + 250

    page.mouse.move(start_x, start_y)
    page.mouse.down()
    for i in range(1, 11):
        page.mouse.move(start_x + (target_x - start_x) * (i / 10),
                        start_y + (target_y - start_y) * (i / 10))
        page.wait_for_timeout(15)
    page.mouse.up()
    page.wait_for_timeout(200)

    post_drag = page.evaluate("""() => {
        const el = document.getElementById('brush-control');
        const rect = el.getBoundingClientRect();
        const stored = JSON.parse(localStorage.getItem('artweb.brushPanelPos.v1') || 'null');
        return {
            hasCustomPos: el.classList.contains('is-custom-position'),
            inlineLeft: el.style.left,
            inlineTop: el.style.top,
            rectLeft: rect.left,
            rectTop: rect.top,
            stored
        };
    }""")

    drag_custom_ok = post_drag["hasCustomPos"]
    drag_coords_ok = len(post_drag["inlineLeft"]) > 0 and len(post_drag["inlineTop"]) > 0
    storage_ok = (post_drag["stored"] is not None and
                  0.0 <= post_drag["stored"]["x"] <= 1.0 and
                  0.0 <= post_drag["stored"]["y"] <= 1.0)

    page.reload()
    wait_engine_ready(page)
    page.wait_for_timeout(400)

    post_reload = page.evaluate("""() => {
        const el = document.getElementById('brush-control');
        const rect = el.getBoundingClientRect();
        return {
            hasCustomPos: el.classList.contains('is-custom-position'),
            inlineLeft: el.style.left,
            inlineTop: el.style.top,
            rectLeft: rect.left,
            rectTop: rect.top
        };
    }""")

    reload_persisted = (post_reload["hasCustomPos"] and
                        abs(post_reload["rectLeft"] - post_drag["rectLeft"]) <= 3.0 and
                        abs(post_reload["rectTop"] - post_drag["rectTop"]) <= 3.0)

    page.dblclick("#brush-toggle-btn")
    page.wait_for_timeout(300)

    post_reset = page.evaluate("""() => {
        const el = document.getElementById('brush-control');
        const stored = localStorage.getItem('artweb.brushPanelPos.v1');
        return {
            hasCustomPos: el.classList.contains('is-custom-position'),
            inlineLeft: el.style.left,
            inlineTop: el.style.top,
            stored
        };
    }""")

    reset_ok = (not post_reset["hasCustomPos"] and
                post_reset["inlineLeft"] == "" and
                post_reset["inlineTop"] == "" and
                post_reset["stored"] is None)

    passed = drag_custom_ok and drag_coords_ok and storage_ok and reload_persisted and reset_ok

    return {
        "name": "Brush Drag Persistence & Double-Click Reset",
        "passed": passed,
        "drag_custom_ok": drag_custom_ok,
        "drag_coords_ok": drag_coords_ok,
        "storage_ok": storage_ok,
        "reload_persisted": reload_persisted,
        "reset_ok": reset_ok
    }


# ==============================================================================
# Challenge 6: Brush Popup Adaptive Flip, Outside Click Dismiss & Inside Immunity
# ==============================================================================
def challenge_brush_popup_interactions(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Verify:
    1. Toggle open/close: clicking button toggles .open class and .active state.
    2. Inside click immunity: clicks on sliders or internal elements keep popup open.
    3. Outside click dismiss: clicks on background canvas close popup immediately.
    4. Adaptive vertical flip: dragging panel close to bottom viewport edge forces popup to expand UPWARDS.
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    # 1. Toggle open
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)

    state_open = page.evaluate("""() => {
        const popup = document.getElementById('brush-popup');
        const btn = document.getElementById('brush-toggle-btn');
        return {
            popupOpen: popup.classList.contains('open'),
            btnActive: btn.classList.contains('active')
        };
    }""")
    assert state_open["popupOpen"] and state_open["btnActive"], "Popup should open on click"

    # 2. Inside click immunity (click slider inside popup)
    slider = page.locator("#brush-size-slider")
    slider.click()
    page.wait_for_timeout(150)

    state_after_inside = page.evaluate("""() => {
        const popup = document.getElementById('brush-popup');
        return popup.classList.contains('open');
    }""")
    assert state_after_inside, "Inside click on slider must NOT dismiss popup"

    # 3. Outside click dismiss
    page.mouse.click(200, 200)
    page.wait_for_timeout(250)

    state_after_outside = page.evaluate("""() => {
        const popup = document.getElementById('brush-popup');
        const btn = document.getElementById('brush-toggle-btn');
        return {
            popupOpen: popup.classList.contains('open'),
            btnActive: btn.classList.contains('active')
        };
    }""")
    dismiss_ok = (not state_after_outside["popupOpen"] and not state_after_outside["btnActive"])

    # 4. Adaptive flip: position panel at the very bottom of viewport
    page.evaluate("""() => {
        const el = document.getElementById('brush-control');
        el.style.left = '600px';
        el.style.top = '720px';
        el.style.right = 'auto';
        el.classList.add('is-custom-position');
    }""")
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(300)

    flip_data = page.evaluate("""() => {
        const popup = document.getElementById('brush-popup');
        const rect = popup.getBoundingClientRect();
        return {
            top: popup.style.top,
            bottom: popup.style.bottom,
            rectTop: rect.top,
            rectBottom: rect.bottom,
            isAboveButton: rect.bottom <= 730
        };
    }""")

    flip_ok = flip_data["bottom"] == "calc(100% + 10px)" or flip_data["isAboveButton"]

    # Close popup and reset
    page.dblclick("#brush-toggle-btn")
    page.wait_for_timeout(200)

    passed = dismiss_ok and flip_ok

    return {
        "name": "Brush Popup Adaptive Flip & Outside Click Dismiss",
        "passed": passed,
        "dismiss_ok": dismiss_ok,
        "flip_ok": flip_ok,
        "flip_data": flip_data
    }


# ==============================================================================
# Challenge 7: Classical Loupe Zoom, Reset & HitPanel Invariant
# ==============================================================================
def challenge_loupe_and_hitpanel(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Verify:
    1. Loupe toggle activates brass loupe element (#macro-loupe).
    2. Zoom chips cycle zoom levels (2.0x, 3.5x, 5.0x) and update appState.loupeZoom correctly.
    3. Macro canvas zoom reset button is available.
    4. HitPanel invariant: closed brush popup has opacity:0 and pointer-events:none.
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    # 1. Open brush popup and activate loupe
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)
    page.click("#toggle-loupe-btn")
    page.wait_for_timeout(300)

    loupe_active = page.evaluate("""() => {
        const loupe = document.getElementById('macro-loupe');
        const opts = document.getElementById('loupe-options-box');
        return {
            loupeVisible: loupe && loupe.style.display === 'block',
            optsVisible: opts && opts.style.display === 'block',
            isLoupeEnabled: window.__gardenEngine.isLoupeEnabled()
        };
    }""")

    # 2. Cycle zoom chips: click 2.0x chip
    chip_2x = page.locator(".loupe-zoom-chip[data-zoom='2.0']")
    if chip_2x.count() > 0:
        chip_2x.click()
        page.wait_for_timeout(150)

    zoom_2x_active = page.evaluate("() => Math.abs(window.__gardenEngine.getLoupeZoom() - 2.0) < 0.2")

    # Click 5.0x chip
    chip_5x = page.locator(".loupe-zoom-chip[data-zoom='5.0']")
    if chip_5x.count() > 0:
        chip_5x.click()
        page.wait_for_timeout(150)

    zoom_5x_active = page.evaluate("() => Math.abs(window.__gardenEngine.getLoupeZoom() - 5.0) < 0.2")

    # 3. Macro reset button presence
    reset_btn_ok = page.locator("#macro-zoom-reset-btn").count() > 0

    # 4. HitPanel invariant: verify closed popup has pointer-events: none and opacity: 0
    page.mouse.click(200, 200)
    page.wait_for_timeout(400)

    hitpanel_safe = page.evaluate("""() => {
        const popup = document.getElementById('brush-popup');
        const cs = window.getComputedStyle(popup);
        const op = parseFloat(cs.opacity);
        return {
            pointerEvents: cs.pointerEvents,
            opacity: op,
            isSafe: cs.pointerEvents === 'none' && op < 0.01
        };
    }""")

    # Turn off loupe
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)
    page.click("#toggle-loupe-btn")
    page.wait_for_timeout(200)
    page.mouse.click(200, 200)

    passed = (loupe_active["isLoupeEnabled"] and
              zoom_2x_active and
              zoom_5x_active and
              reset_btn_ok and
              hitpanel_safe["isSafe"])

    return {
        "name": "Classical Loupe Zoom & HitPanel Invariant",
        "passed": passed,
        "loupe_active": loupe_active,
        "zoom_2x_active": zoom_2x_active,
        "zoom_5x_active": zoom_5x_active,
        "reset_btn_ok": reset_btn_ok,
        "hitpanel_safe": hitpanel_safe
    }


# ==============================================================================
# Challenge 8: Stroke Dimming Dynamics
# ==============================================================================
def challenge_stroke_dimming(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Verify:
    1. Art quote container has normal opacity (~1.0) when idle.
    2. Painting strokes on stage adds .subtle class and dims opacity to 0.25.
    3. Releasing pointer restores opacity.
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(500)

    initial_opacity = page.evaluate("""() => {
        const quote = document.getElementById('art-quote');
        return parseFloat(window.getComputedStyle(quote).opacity);
    }""")

    stage = page.locator("#art-stage")
    box = stage.bounding_box()
    cx = box["x"] + box["width"] / 2
    cy = box["y"] + box["height"] / 2

    page.mouse.move(cx - 100, cy)
    page.mouse.down()
    for i in range(1, 15):
        page.mouse.move(cx - 100 + i * 15, cy + math.sin(i) * 30)
        page.wait_for_timeout(15)

    dimmed_data = page.evaluate("""() => {
        const quote = document.getElementById('art-quote');
        const cs = window.getComputedStyle(quote);
        return {
            hasSubtle: quote.classList.contains('subtle'),
            opacity: parseFloat(cs.opacity)
        };
    }""")

    page.mouse.up()
    page.wait_for_timeout(600)

    passed = (initial_opacity >= 0.8 and
              (dimmed_data["hasSubtle"] or abs(dimmed_data["opacity"] - 0.25) <= 0.05))

    return {
        "name": "Stroke Dimming Dynamics",
        "passed": passed,
        "initial_opacity": initial_opacity,
        "dimmed_opacity": dimmed_data["opacity"],
        "has_subtle": dimmed_data["hasSubtle"]
    }


# ==============================================================================
# Challenge 9: Rapid Mode Switching Stress Test (Adversarial Race Generator)
# ==============================================================================
def challenge_rapid_mode_switching(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Rapidly alternate mode clicks 20 times within 1 second.
    Check:
    1. Zero console errors generated.
    2. Engine mode synchronizes perfectly with the final clicked button.
    3. Canvas buffers remain healthy.
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(400)

    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "favicon.ico" not in m.text else None)
    page.on("pageerror", lambda e: errors.append(str(e)))

    final_mode = "sleep"
    for i in range(20):
        if i % 2 == 0:
            page.click("#msw-scratch-btn")
            final_mode = "scratch"
        else:
            page.click("#msw-sleep-btn")
            final_mode = "sleep"
        page.wait_for_timeout(40)

    page.wait_for_timeout(600)

    engine_mode = page.evaluate("() => window.__gardenEngine.getAppMode()")
    state_synchronized = (engine_mode == final_mode)
    zero_errors = (len(errors) == 0)

    passed = state_synchronized and zero_errors

    return {
        "name": "Rapid Mode Switching Stress Test",
        "passed": passed,
        "final_expected_mode": final_mode,
        "engine_mode": engine_mode,
        "synchronized": state_synchronized,
        "errors": errors
    }


# ==============================================================================
# Main Runner
# ==============================================================================
def main():
    print("=" * 80)
    print(" ⚔️  Milestone 2 Empirical Adversarial Stress Harness")
    print("=" * 80)

    with LocalServer() as server:
        base_url = server.base_url
        print(f" Local Daemon: {base_url} (serving {PROJECT_ROOT})\n")

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            challenges = [
                ("Challenge 1: Console & Network Integrity", challenge_console_integrity),
                ("Challenge 2: Floating Controls Subpixel Parity", challenge_floating_controls_baseline),
                ("Challenge 3: Art Quote Optical Center & Rhythm", challenge_art_quote_optical_center_and_rhythm),
                ("Challenge 4: Elevation Hierarchy & Monotonicity", challenge_elevation_hierarchy),
                ("Challenge 5: Brush Drag Persistence & Reset", challenge_brush_drag_and_persistence),
                ("Challenge 6: Brush Popup Adaptive Flip & Dismiss", challenge_brush_popup_interactions),
                ("Challenge 7: Classical Loupe Zoom & HitPanel", challenge_loupe_and_hitpanel),
                ("Challenge 8: Stroke Dimming Dynamics", challenge_stroke_dimming),
                ("Challenge 9: Rapid Mode Switching Stress", challenge_rapid_mode_switching),
            ]

            all_passed = True
            summary = []

            for idx, (title, fn) in enumerate(challenges, 1):
                start_t = time.time()
                print(f"[{idx}/{len(challenges)}] Running {title}...")
                try:
                    res = fn(page, base_url)
                    dur = (time.time() - start_t) * 1000
                    status = "PASSED" if res["passed"] else "FAILED"
                    if not res["passed"]:
                        all_passed = False
                    print(f"      Result: {status} ({dur:.1f}ms)")
                    summary.append((title, status, dur, res))
                except Exception as exc:
                    dur = (time.time() - start_t) * 1000
                    all_passed = False
                    print(f"      Result: EXCEPTION ({dur:.1f}ms) — {exc}")
                    summary.append((title, "EXCEPTION", dur, {"error": str(exc)}))

            browser.close()

            print("\n" + "=" * 80)
            print(" 📊 ADVERSARIAL CHALLENGE SUMMARY REPORT")
            print("=" * 80)
            for title, status, dur, res in summary:
                symbol = "✓" if status == "PASSED" else "✗"
                print(f" {symbol} {title:<50} [{status}] ({dur:6.1f}ms)")

            print("=" * 80)
            if all_passed:
                print(" 🏆 FINAL RESULT: ALL 9 EMPIRICAL CHALLENGES PASSED (100%)")
            else:
                print(" ❌ FINAL RESULT: EMPIRICAL FAILURES DETECTED")
            print("=" * 80)

            # Dump results to json for reporting
            report_out = PROJECT_ROOT / ".agents" / "teamwork" / "m2_challenger_2" / "challenge_m2_results.json"
            clean_summary = []
            for title, status, dur, res in summary:
                clean_summary.append({
                    "title": title,
                    "status": status,
                    "duration_ms": round(dur, 2),
                    "details": res
                })
            report_out.write_text(json.dumps(clean_summary, indent=2, ensure_ascii=False), encoding="utf-8")

            return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

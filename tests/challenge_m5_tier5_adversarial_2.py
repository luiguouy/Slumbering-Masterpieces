#!/usr/bin/env python3
"""
challenge_m5_tier5_adversarial_2.py - Dedicated Playwright Adversarial Test Suite for Tier 5.
Authored by: m5_challenger_2 (Adversarial Empirical Verifier — Tier 5: Interaction Stress & Deep Visual Containment)

Target Domains:
1. Macro-loupe physical boundary clamping: Viewport physical edges (x=0, y=0, x=stageWidth, y=stageHeight)
   across widescreen (220px loupe) and mobile/tablet (180px loupe); zero overflow scrollbars.
2. Concurrent interaction thrashing: High-frequency interleaved mode switches (Sleep <-> Scratch,
   Loupe on/off, FullColor, Fit modes, Zoom) with concurrent drawer animations; zero freezes or console errors.
3. Canvas drawing & pointer event isolation: Stroke execution verification, and rigorous testing of
   pointer event isolation over panels and backdrops (detecting backdrop pointer blocking vs ghost draws).
4. Virtual scrolling stress: High-speed scrolling through 420 masterpieces in Gallery drawer;
   verifying batch loading, zero collapsed cards, and strict 4:3 aspect ratio containment.
5. CJK typography extreme length stress: 100+ character CJK titles, authors, and narrative blocks;
   verifying text-wrap: balance/pretty, zero vertical text collision/overlap, and zero horizontal document overflow.
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
from playwright.sync_api import sync_playwright, Page, Browser


def wait_engine_ready(page: Page, timeout: int = 15000):
    page.wait_for_function(
        "() => window.__gardenEngine && typeof window.__gardenEngine.isLoaded === 'function' && window.__gardenEngine.isLoaded()",
        timeout=timeout
    )


# ------------------------------------------------------------------------------
# Test 1: Macro-Loupe Boundary Clamping Across Form Factors
# ------------------------------------------------------------------------------
def test_macro_loupe_boundary_clamping(page: Page, base_url: str) -> Dict[str, Any]:
    viewports = [
        {"name": "Widescreen Desktop", "width": 1920, "height": 1080, "expected_diameter": 220},
        {"name": "Tablet Portrait", "width": 768, "height": 1024, "expected_diameter": 220},
        {"name": "Mobile Standard", "width": 390, "height": 844, "expected_diameter": 180}
    ]

    checks = []
    overall_pass = True

    for vp in viewports:
        w, h, expected_d = vp["width"], vp["height"], vp["expected_diameter"]
        page.set_viewport_size({"width": w, "height": h})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        page.wait_for_timeout(200)

        # Set cover mode and enable loupe to guarantee artwork under test coordinates
        page.evaluate("""() => {
            window.__gardenEngine.setFitMode('cover');
            window.__gardenEngine.toggleLoupe(true);
        }""")
        page.wait_for_timeout(150)

        # 8 physical boundary points
        edge_points = [
            ("Top-Left", 0, 0),
            ("Top-Edge", w // 2, 0),
            ("Top-Right", w, 0),
            ("Left-Edge", 0, h // 2),
            ("Right-Edge", w, h // 2),
            ("Bottom-Left", 0, h),
            ("Bottom-Edge", w // 2, h),
            ("Bottom-Right", w, h)
        ]

        vp_checks = []
        for name, px, py in edge_points:
            edge_data = page.evaluate("""(pos) => {
                const stage = document.getElementById('art-stage');
                const ev = new MouseEvent('mousemove', { clientX: pos.x, clientY: pos.y, bubbles: true });
                stage.dispatchEvent(ev);

                const doc = document.documentElement;
                const body = document.body;
                const loupe = document.getElementById('macro-loupe');
                const rect = loupe ? loupe.getBoundingClientRect() : null;

                const hasHOverflow = (doc.scrollWidth > window.innerWidth) || (body.scrollWidth > window.innerWidth);
                const hasVOverflow = (doc.scrollHeight > window.innerHeight) || (body.scrollHeight > window.innerHeight);

                return {
                    pos,
                    hasHOverflow,
                    hasVOverflow,
                    docScrollW: doc.scrollWidth,
                    docScrollH: doc.scrollHeight,
                    vw: window.innerWidth,
                    vh: window.innerHeight,
                    loupeWidth: rect ? rect.width : 0,
                    loupeHeight: rect ? rect.height : 0,
                    loupeActive: loupe ? loupe.classList.contains('active') : false
                };
            }""", {"x": px, "y": py})

            # Check: zero overflow scrollbars
            no_overflow = (not edge_data["hasHOverflow"]) and (not edge_data["hasVOverflow"])
            # Check: diameter matches expected form factor
            size_ok = abs(edge_data["loupeWidth"] - expected_d) <= 1.0

            point_pass = no_overflow and size_ok
            if not point_pass:
                overall_pass = False

            vp_checks.append({
                "point": name,
                "coords": (px, py),
                "passed": point_pass,
                "no_overflow": no_overflow,
                "size_ok": size_ok,
                "actual_diameter": edge_data["loupeWidth"],
                "expected_diameter": expected_d
            })

        checks.append({
            "viewport": vp["name"],
            "resolution": f"{w}x{h}",
            "passed": all(c["passed"] for c in vp_checks),
            "edge_checks": vp_checks
        })

    return {
        "name": "Macro-Loupe Boundary Clamping & Zero Scrollbar Leak",
        "passed": overall_pass,
        "details": checks
    }


# ------------------------------------------------------------------------------
# Test 2: Concurrent Interaction Thrashing
# ------------------------------------------------------------------------------
def test_concurrent_interaction_thrashing(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    console_errors: List[str] = []
    page_errors: List[str] = []

    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" and "favicon.ico" not in m.text else None)
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    # Execute 30 rapid interleaved state changes
    iterations = 30
    thrash_log = []

    for i in range(iterations):
        action = i % 6
        if action == 0:
            # Switch to scratch mode & stroke
            page.evaluate("() => window.__gardenEngine.setAppMode('scratch')")
            page.mouse.move(700, 400)
            page.mouse.down()
            page.mouse.move(750, 420)
            page.mouse.up()
            thrash_log.append("mode_scratch_stroke")
        elif action == 1:
            # Open and close gallery quickly
            page.evaluate("() => window.__gardenEngine.openGallery()")
            page.wait_for_timeout(15)
            page.evaluate("() => window.__gardenEngine.closeGallery()")
            thrash_log.append("gallery_toggle")
        elif action == 2:
            # Toggle loupe and adjust zoom
            page.evaluate("() => window.__gardenEngine.toggleLoupe(true)")
            page.evaluate("() => window.__gardenEngine.cycleLoupeZoom()")
            page.mouse.move(600, 350)
            thrash_log.append("loupe_cycle")
        elif action == 3:
            # Open story drawer & toggle fit mode
            page.evaluate("() => window.__gardenEngine.openStory()")
            page.wait_for_timeout(15)
            page.evaluate("() => window.__gardenEngine.setFitMode('contain')")
            page.evaluate("() => window.__gardenEngine.closeStory()")
            thrash_log.append("story_fit_toggle")
        elif action == 4:
            # Macro zoom in & reset
            page.evaluate("() => window.__gardenEngine.setMacroZoom(2.8)")
            page.evaluate("() => window.__gardenEngine.resetMacroZoom(true)")
            thrash_log.append("macro_zoom_reset")
        elif action == 5:
            # Switch back to sleep mode & toggle full color
            page.evaluate("() => window.__gardenEngine.setAppMode('sleep')")
            page.evaluate("() => window.__gardenEngine.toggleFullColor()")
            page.wait_for_timeout(10)
            page.evaluate("() => window.__gardenEngine.toggleFullColor()")
            thrash_log.append("sleep_bloom_toggle")

    page.wait_for_timeout(400)

    # Post-thrash engine health audit
    health = page.evaluate("""() => {
        const bgCanvas = document.getElementById('bg-canvas');
        const revealCanvas = document.getElementById('reveal-canvas');
        const mswSleep = document.getElementById('msw-sleep-btn');
        const mswScratch = document.getElementById('msw-scratch-btn');
        const currentMode = window.__gardenEngine.getAppMode();

        const sleepActive = mswSleep.classList.contains('active');
        const scratchActive = mswScratch.classList.contains('active');

        // Check if mode switcher active state strictly matches appMode
        const modeSyncOk = (currentMode === 'sleep' && sleepActive && !scratchActive) ||
                           (currentMode === 'scratch' && scratchActive && !sleepActive);

        return {
            isLoaded: window.__gardenEngine.isLoaded(),
            currentMode,
            modeSyncOk,
            hasBgCanvas: Boolean(bgCanvas && bgCanvas.width > 0 && bgCanvas.height > 0),
            hasRevealCanvas: Boolean(revealCanvas && revealCanvas.width > 0 && revealCanvas.height > 0),
            isScratchLocked: window.__gardenEngine.isScratchLocked()
        };
    }""")

    passed = (
        len(console_errors) == 0 and
        len(page_errors) == 0 and
        health["isLoaded"] and
        health["modeSyncOk"] and
        health["hasBgCanvas"] and
        health["hasRevealCanvas"] and
        not health["isScratchLocked"]
    )

    return {
        "name": "Concurrent Interaction Thrashing & State Synchronization",
        "passed": passed,
        "iterations_completed": iterations,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "health_audit": health
    }


# ------------------------------------------------------------------------------
# Test 3: Canvas Drawing & Pointer Event Isolation
# ------------------------------------------------------------------------------
def test_pointer_event_isolation_and_ghost_draws(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    checks = []

    # Phase A: Canvas drawing works normally when no overlays are active
    phase_a = page.evaluate("""() => {
        window.__gardenEngine.setAppMode('scratch');
        const r0 = window.__gardenEngine.getScratchRatio();
        
        // Stroke directly on stage center
        window.__gardenEngine.stroke(500, 400, 600, 450);
        const r1 = window.__gardenEngine.getScratchRatio();
        
        return {
            initialRatio: r0,
            postRatio: r1,
            stroked: r1 > r0
        };
    }""")
    checks.append({
        "phase": "canvas_normal_stroke_response",
        "passed": phase_a["stroked"],
        "details": phase_a
    })

    # Phase B: Pointer event isolation over Gallery Drawer Backdrop
    # When Gallery is open, moving pointer on #gallery-backdrop MUST NOT draw on canvas below.
    phase_b = page.evaluate("""() => {
        window.__gardenEngine.setAppMode('scratch');
        window.__gardenEngine.openGallery();
        
        const initialRatio = window.__gardenEngine.getScratchRatio();
        const backdrop = document.getElementById('gallery-backdrop');
        const cursor = document.getElementById('custom-cursor');
        
        // Dispatch mousemove events across backdrop (x=1050 to 1250, outside 75vw panel)
        for (let x = 1050; x <= 1250; x += 20) {
            const ev = new MouseEvent('mousemove', { clientX: x, clientY: 400, bubbles: true });
            backdrop.dispatchEvent(ev);
        }
        
        const postRatio = window.__gardenEngine.getScratchRatio();
        const ghostDrawn = postRatio > initialRatio;
        const cursorUnveiled = cursor ? (cursor.style.opacity === '1' || cursor.classList.contains('active')) : false;

        window.__gardenEngine.closeGallery();

        return {
            initialRatio,
            postRatio,
            ghostDrawn,
            cursorUnveiled,
            isIsolated: (!ghostDrawn && !cursorUnveiled)
        };
    }""")
    checks.append({
        "phase": "gallery_backdrop_pointer_isolation",
        "passed": phase_b["isIsolated"],
        "details": phase_b
    })

    # Phase C: Pointer event isolation over Story Drawer Backdrop
    phase_c = page.evaluate("""() => {
        window.__gardenEngine.setAppMode('scratch');
        window.__gardenEngine.openStory();
        
        const initialRatio = window.__gardenEngine.getScratchRatio();
        const backdrop = document.getElementById('story-backdrop');
        const cursor = document.getElementById('custom-cursor');
        
        // Story panel is on the right; backdrop is on the left (e.g. x=200, y=400)
        for (let x = 100; x <= 300; x += 20) {
            const ev = new MouseEvent('mousemove', { clientX: x, clientY: 400, bubbles: true });
            backdrop.dispatchEvent(ev);
        }
        
        const postRatio = window.__gardenEngine.getScratchRatio();
        const ghostDrawn = postRatio > initialRatio;
        const cursorUnveiled = cursor ? (cursor.style.opacity === '1' || cursor.classList.contains('active')) : false;

        window.__gardenEngine.closeStory();

        return {
            initialRatio,
            postRatio,
            ghostDrawn,
            cursorUnveiled,
            isIsolated: (!ghostDrawn && !cursorUnveiled)
        };
    }""")
    checks.append({
        "phase": "story_backdrop_pointer_isolation",
        "passed": phase_c["isIsolated"],
        "details": phase_c
    })

    # Phase D: Pointer event isolation over Help Modal Backdrop
    phase_d = page.evaluate("""() => {
        window.__gardenEngine.setAppMode('scratch');
        window.__gardenEngine.openHelp();
        
        const initialRatio = window.__gardenEngine.getScratchRatio();
        const backdrop = document.getElementById('help-backdrop');
        const cursor = document.getElementById('custom-cursor');
        
        // Help dialog is centered; backdrop is at periphery (e.g. x=50, y=50)
        for (let x = 20; x <= 120; x += 10) {
            const ev = new MouseEvent('mousemove', { clientX: x, clientY: 50, bubbles: true });
            backdrop.dispatchEvent(ev);
        }
        
        const postRatio = window.__gardenEngine.getScratchRatio();
        const ghostDrawn = postRatio > initialRatio;
        const cursorUnveiled = cursor ? (cursor.style.opacity === '1' || cursor.classList.contains('active')) : false;

        window.__gardenEngine.closeHelp();

        return {
            initialRatio,
            postRatio,
            ghostDrawn,
            cursorUnveiled,
            isIsolated: (!ghostDrawn && !cursorUnveiled)
        };
    }""")
    checks.append({
        "phase": "help_backdrop_pointer_isolation",
        "passed": phase_d["isIsolated"],
        "details": phase_d
    })

    all_passed = all(c["passed"] for c in checks)
    return {
        "name": "Canvas Drawing & Pointer Event Isolation Under Drawers/Modals",
        "passed": all_passed,
        "details": checks
    }


# ------------------------------------------------------------------------------
# Test 4: Virtual Scrolling Stress Across 420 Masterpieces
# ------------------------------------------------------------------------------
def test_virtual_scrolling_stress_420_cards(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(350)

    # Scroll high-speed to batch-load all 420 cards
    scroll_res = page.evaluate("""async () => {
        const container = document.getElementById('gallery-list-container');
        const total = window.__gardenEngine.getMasterpieces().length;

        let lastCount = 0;
        let stagnationAttempts = 0;
        const maxScrollLoops = 40;

        for (let loop = 0; loop < maxScrollLoops; loop++) {
            const cards = container.querySelectorAll('.gallery-card');
            if (cards.length >= total) break;

            container.scrollTop = container.scrollHeight;
            await new Promise(resolve => setTimeout(resolve, 50));

            if (cards.length === lastCount) {
                stagnationAttempts++;
                if (stagnationAttempts >= 6) break;
            } else {
                stagnationAttempts = 0;
                lastCount = cards.length;
            }
        }

        const cards = container.querySelectorAll('.gallery-card');
        let collapsedCards = 0;
        let invalidAspectCards = 0;
        const ratios = [];

        cards.forEach(card => {
            const thumbBox = card.querySelector('.card-thumb-box');
            if (!thumbBox) {
                collapsedCards++;
                return;
            }
            const rect = thumbBox.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0) {
                collapsedCards++;
                return;
            }

            const ratio = rect.width / rect.height;
            ratios.push(ratio);
            // Verify strictly adheres to 4:3 = 1.333 within 0.05 tolerance
            if (Math.abs(ratio - (4.0 / 3.0)) > 0.05) {
                invalidAspectCards++;
            }
        });

        // Test card switching interactivity from batch 15 (e.g. card #300)
        let switchedSuccessfully = false;
        const targetIndex = 300;
        const targetCard = container.querySelector(`.gallery-card[data-index="${targetIndex}"]`);
        if (targetCard) {
            targetCard.click();
            switchedSuccessfully = (window.__gardenEngine.getCurrentIndex() === targetIndex);
        }

        const sentinel = container.querySelector('.gallery-scroll-sentinel');
        const sentinelHiddenWhenComplete = sentinel ? (sentinel.style.display === 'none') : true;

        return {
            totalExpected: total,
            totalRendered: cards.length,
            collapsedCards,
            invalidAspectCards,
            minRatio: ratios.length ? Math.min(...ratios) : 0,
            maxRatio: ratios.length ? Math.max(...ratios) : 0,
            switchedSuccessfully,
            sentinelHiddenWhenComplete
        };
    }""")

    page.evaluate("() => window.__gardenEngine.closeGallery()")

    passed = (
        scroll_res["totalRendered"] == scroll_res["totalExpected"] and
        scroll_res["collapsedCards"] == 0 and
        scroll_res["invalidAspectCards"] == 0 and
        scroll_res["switchedSuccessfully"] and
        scroll_res["sentinelHiddenWhenComplete"]
    )

    return {
        "name": "Virtual Scrolling Stress Through 420 Masterpieces",
        "passed": passed,
        "details": scroll_res
    }


# ------------------------------------------------------------------------------
# Test 5: CJK Typography Extreme Length Stress (100+ CJK Characters)
# ------------------------------------------------------------------------------
def test_cjk_typography_extreme_length_stress(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    typography_audit = page.evaluate("""() => {
        const quoteEl = document.querySelector('#art-quote .quote-text');
        const authorEl = document.querySelector('#art-quote .quote-author');
        const quoteContainer = document.getElementById('art-quote');
        
        // 1. Extreme 112-character CJK philosophical quote
        const extremeQuote = '艺术并不超越大自然，不过会使大自然更美化。名画不仅是视觉的愉悦，更承载着人类文明深邃的历史哲思与精神寄托。当观者驻足凝视画布上的每一道笔触、每一抹色彩与每一缕晨曦，皆能跨越时光长河与大师心灵共鸣。美是真理的光芒，简练即至美。';
        // 2. Extreme 42-character author accreditation
        const extremeAuthor = '列奥纳多·迪·皮耶罗·达·芬奇 · 意大利文艺复兴三杰之首 · 博学全能的世纪先驱';
        
        const origQuote = quoteEl.textContent;
        const origAuthor = authorEl.textContent;

        quoteEl.textContent = extremeQuote;
        authorEl.textContent = extremeAuthor;

        const qRect = quoteEl.getBoundingClientRect();
        const aRect = authorEl.getBoundingClientRect();
        const cRect = quoteContainer.getBoundingClientRect();
        const vw = window.innerWidth;
        const docScrollW = document.documentElement.scrollWidth;

        const qComputed = window.getComputedStyle(quoteEl);
        const aComputed = window.getComputedStyle(authorEl);

        // Verification 1: text-wrap balance / pretty active
        const hasTextWrapBalance = qComputed.textWrap === 'balance' || qComputed.textWrap === 'pretty';

        // Verification 2: Zero text overlap / vertical collision
        const isOverlapping = aRect.top < (qRect.bottom - 1.0);
        const verticalGap = aRect.top - qRect.bottom;

        // Verification 3: Container max-width bounded within viewport
        const maxAllowedWidth = Math.min(768, vw - 64) + 2.0;
        const containerBounded = cRect.width <= maxAllowedWidth;

        // Verification 4: Zero horizontal document scrollbar leak
        const hasOverflow = docScrollW > vw;

        // Verification 5: Line-height baseline closure remains structured (36px for xl, 24px for sm)
        const quoteLh = parseFloat(qComputed.lineHeight);
        const authorLh = parseFloat(aComputed.lineHeight);
        const baselineClosureOk = (quoteLh >= 30.0) && (authorLh >= 20.0);

        // 3. Test Story Drawer Extreme Narrative
        window.__gardenEngine.openStory();
        const storyTitle = document.getElementById('story-title');
        const storyNarrative = document.getElementById('story-narrative');
        const storyPanel = document.querySelector('.story-panel');

        const extremeStoryTitle = '蒙娜丽莎的永恒微笑与卢浮宫神秘防弹玻璃后的数百年艺术谜团';
        const extremeStoryNarrative = '达芬奇以精湛绝伦的晕涂法描绘出这位佛罗伦萨丝绸商人妻子的神秘微笑。五百年来，无数艺术史家、科学家与观者试图解构其眼角与唇线间的微光神采。在层层油彩堆叠与半透明罩染的交织下，光影变幻宛如晨雾消散。无论从展厅的哪一个角度凝望，她的目光都深情地凝视着你，宛若穿越时空永恒不息的灵魂对话。';

        if (storyTitle) storyTitle.textContent = extremeStoryTitle;
        if (storyNarrative) storyNarrative.textContent = extremeStoryNarrative;

        const sTitleRect = storyTitle ? storyTitle.getBoundingClientRect() : null;
        const sPanelRect = storyPanel ? storyPanel.getBoundingClientRect() : null;
        const sNarrativeComputed = storyNarrative ? window.getComputedStyle(storyNarrative) : null;

        const storyTitleInBounds = (sTitleRect && sPanelRect) ? (sTitleRect.right <= sPanelRect.right + 2.0) : true;
        const storyNarrativePretty = sNarrativeComputed ? (sNarrativeComputed.textWrap === 'pretty' || sNarrativeComputed.textWrap === 'wrap') : true;
        const storyOverflow = document.documentElement.scrollWidth > vw;

        window.__gardenEngine.closeStory();

        // Restore originals
        quoteEl.textContent = origQuote;
        authorEl.textContent = origAuthor;

        return {
            hasTextWrapBalance,
            isOverlapping,
            verticalGap,
            containerWidth: cRect.width,
            maxAllowedWidth,
            containerBounded,
            hasOverflow,
            baselineClosureOk,
            quoteLh,
            authorLh,
            storyTitleInBounds,
            storyNarrativePretty,
            storyOverflow
        };
    }""")

    passed = (
        typography_audit["hasTextWrapBalance"] and
        (not typography_audit["isOverlapping"]) and
        typography_audit["containerBounded"] and
        (not typography_audit["hasOverflow"]) and
        typography_audit["baselineClosureOk"] and
        typography_audit["storyTitleInBounds"] and
        (not typography_audit["storyOverflow"])
    )

    return {
        "name": "CJK Typography Extreme Length Stress (100+ Chars)",
        "passed": passed,
        "details": typography_audit
    }


# ------------------------------------------------------------------------------
# Main Runner & CLI
# ------------------------------------------------------------------------------
def main():
    print("=" * 80)
    print(" ⚔️  Milestone 5 Tier 5 Adversarial Stress & Visual Containment Suite")
    print("    Author: m5_challenger_2")
    print("=" * 80)

    results = []
    overall_suite_pass = True

    with LocalServer() as server:
        base_url = server.base_url
        print(f" Local HTTP Server: {base_url}\n")

        with sync_playwright() as p:
            # Launch Chrome channel for Windows environment compatibility
            browser: Browser = p.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context()
            page = context.new_page()

            test_cases = [
                ("1. Macro-Loupe Boundary Clamping", test_macro_loupe_boundary_clamping),
                ("2. Concurrent Interaction Thrashing", test_concurrent_interaction_thrashing),
                ("3. Pointer Event Isolation & Ghost Draws", test_pointer_event_isolation_and_ghost_draws),
                ("4. Virtual Scrolling Stress (420 Masterpieces)", test_virtual_scrolling_stress_420_cards),
                ("5. CJK Typography Extreme Length Stress", test_cjk_typography_extreme_length_stress)
            ]

            for label, test_fn in test_cases:
                print(f"▶ Executing {label}...")
                t0 = time.time()
                try:
                    res = test_fn(page, base_url)
                    dur = (time.time() - t0) * 1000
                    status = "PASSED" if res["passed"] else "FAILED"
                    if not res["passed"]:
                        overall_suite_pass = False
                    print(f"  [{status}] {res['name']} ({dur:.1f}ms)")
                    results.append({"name": res["name"], "status": status, "duration_ms": dur, "data": res})
                except Exception as ex:
                    dur = (time.time() - t0) * 1000
                    overall_suite_pass = False
                    print(f"  [ERROR] {label} failed with exception: {ex}")
                    results.append({"name": label, "status": "ERROR", "duration_ms": dur, "error": str(ex)})

            browser.close()

    print("\n" + "=" * 80)
    print(f" 📊 TIER 5 ADVERSARIAL SUITE SUMMARY: {'PASSED' if overall_suite_pass else 'FAILED (DEFECTS DETECTED)'}")
    print("=" * 80)
    for r in results:
        print(f" - [{r['status']}] {r['name']} ({r['duration_ms']:.1f}ms)")
    print("=" * 80)

    # Save structured results
    out_dir = PROJECT_ROOT / ".agents" / "teamwork" / "m5_challenger_2"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / "tier5_results.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({"overall_pass": overall_suite_pass, "tests": results}, f, indent=2, ensure_ascii=False)
    print(f" Report written to: {report_file}")

    # Return exit code matching overall pass status
    sys.exit(0 if overall_suite_pass else 1)


if __name__ == "__main__":
    main()

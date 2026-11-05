#!/usr/bin/env python3
"""
challenge_m4_cascade.py - Empirical Responsive Breakpoint Cascade & Math Verification Harness.

Executed by: m4_challenger_1 (Empirical Challenger)
Canonical Viewports Tested:
1. Widescreen: 1920x1080 (12 columns)
2. Desktop: 1440x900 (12/8 columns)
3. Standard Desktop: 1280x800 (12/8 columns)
4. Tablet Landscape: 1024x768 (8/4 columns)
5. Tablet Portrait: 768x1024 (4 columns)
6. Boundary Tablet: 641x1024 (2 columns)
7. Boundary Mobile: 640x1024 (1 column)
8. Mobile Standard: 375x667 (2/1 columns)
9. Ultra-compact Mobile: 320x568 (1 column, 0 horizontal overflow)
"""

import json
import math
import sys
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


CANONICAL_VIEWPORTS = [
    {"name": "Widescreen", "width": 1920, "height": 1080, "expected_grid_cols": 12, "expected_gallery_cols": 3, "story_type": "side"},
    {"name": "Desktop", "width": 1440, "height": 900, "expected_grid_cols": 12, "expected_gallery_cols": 3, "story_type": "side"},
    {"name": "Standard Desktop", "width": 1280, "height": 800, "expected_grid_cols": 12, "expected_gallery_cols": 3, "story_type": "side"},
    {"name": "Tablet Landscape", "width": 1024, "height": 768, "expected_grid_cols": 8, "expected_gallery_cols": 3, "story_type": "side"},
    {"name": "Tablet Portrait", "width": 768, "height": 1024, "expected_grid_cols": 8, "expected_gallery_cols": 2, "story_type": "side"},
    {"name": "Boundary Tablet", "width": 641, "height": 1024, "expected_grid_cols": 4, "expected_gallery_cols": 2, "story_type": "side"},
    {"name": "Boundary Mobile", "width": 640, "height": 1024, "expected_grid_cols": 4, "expected_gallery_cols": 1, "story_type": "sheet"},
    {"name": "Mobile Standard", "width": 375, "height": 667, "expected_grid_cols": 2, "expected_gallery_cols": 1, "story_type": "sheet"},
    {"name": "Ultra-compact Mobile", "width": 320, "height": 568, "expected_grid_cols": 2, "expected_gallery_cols": 1, "story_type": "sheet"},
]


def run_cascade_verification():
    print("=" * 80)
    print(" 📐 EMPIRICAL CHALLENGER: Milestone 4 Responsive Breakpoint Cascade Harness")
    print("=" * 80)

    results = []

    with LocalServer() as server:
        base_url = server.base_url
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page()

            for vp in CANONICAL_VIEWPORTS:
                w, h = vp["width"], vp["height"]
                page.set_viewport_size({"width": w, "height": h})
                page.goto(f"{base_url}/index.html")
                wait_engine_ready(page)
                page.wait_for_timeout(200)

                # 1. Document & Stage Overflow Check
                overflow_data = page.evaluate("""() => {
                    const docEl = document.documentElement;
                    const body = document.body;
                    const stage = document.getElementById('art-stage');
                    const rootComputed = window.getComputedStyle(docEl);
                    const colsVar = parseInt(rootComputed.getPropertyValue('--grid-columns')) || 12;
                    const gutterVar = rootComputed.getPropertyValue('--grid-gutter').trim();
                    const marginVar = rootComputed.getPropertyValue('--grid-margin').trim();

                    const docScrollW = docEl.scrollWidth;
                    const bodyScrollW = body.scrollWidth;
                    const winW = window.innerWidth;
                    const hasHorizontalOverflow = (docScrollW > winW) || (bodyScrollW > winW);

                    return {
                        winW,
                        winH: window.innerHeight,
                        docScrollW,
                        bodyScrollW,
                        hasHorizontalOverflow,
                        colsVar,
                        gutterVar,
                        marginVar
                    };
                }""")

                # 2. Gallery Drawer Verification
                page.evaluate("() => window.__gardenEngine.openGallery()")
                page.wait_for_timeout(450)

                gallery_data = page.evaluate("""() => {
                    const panel = document.querySelector('.gallery-panel');
                    const container = document.getElementById('gallery-list-container');
                    const cStyle = window.getComputedStyle(container);
                    const cols = cStyle.gridTemplateColumns.split(' ').length;
                    const cards = Array.from(document.querySelectorAll('.gallery-card'));
                    const panelRect = panel.getBoundingClientRect();
                    const containerRect = container.getBoundingClientRect();

                    const hasInternalOverflow = container.scrollWidth > container.clientWidth;
                    const panelOverflow = panel.scrollWidth > panel.clientWidth;

                    return {
                        panelWidth: Math.round(panelRect.width),
                        containerWidth: Math.round(containerRect.width),
                        detectedColumns: cols,
                        cardCount: cards.length,
                        firstCardWidth: cards.length > 0 ? Math.round(cards[0].getBoundingClientRect().width) : 0,
                        hasInternalOverflow,
                        panelOverflow
                    };
                }""")
                page.evaluate("() => window.__gardenEngine.closeGallery()")
                page.wait_for_timeout(200)

                # 3. Story Drawer Verification
                page.evaluate("() => window.__gardenEngine.openStory()")
                page.wait_for_timeout(450)

                story_data = page.evaluate("""() => {
                    const drawer = document.getElementById('story-drawer');
                    const panel = document.querySelector('.story-panel');
                    const handle = document.querySelector('.story-sheet-handle');
                    const narrative = document.getElementById('story-narrative-box');
                    const panelRect = panel.getBoundingClientRect();
                    const pStyle = window.getComputedStyle(panel);
                    const handleStyle = handle ? window.getComputedStyle(handle) : null;
                    const isBottomSheet = handleStyle ? (handleStyle.display !== 'none') : false;

                    return {
                        panelWidth: Math.round(panelRect.width),
                        panelHeight: Math.round(panelRect.height),
                        isBottomSheet,
                        narrativeWidth: narrative ? Math.round(narrative.getBoundingClientRect().width) : 0
                    };
                }""")
                page.evaluate("() => window.__gardenEngine.closeStory()")
                page.wait_for_timeout(200)

                # 4. Help Modal Verification & Optical Centroid
                page.evaluate("() => window.__gardenEngine.openHelp()")
                page.wait_for_timeout(450)

                help_data = page.evaluate("""() => {
                    const dialog = document.querySelector('.help-dialog');
                    const closeBtn = document.getElementById('help-close-btn');
                    const dRect = dialog.getBoundingClientRect();
                    const bRect = closeBtn.getBoundingClientRect();
                    const centroidY = dRect.top + dRect.height / 2.0;
                    const opticalRatio = (centroidY / window.innerHeight) * 100.0;

                    return {
                        dialogWidth: Math.round(dRect.width),
                        dialogHeight: Math.round(dRect.height),
                        btnWidth: Math.round(bRect.width),
                        btnHeight: Math.round(bRect.height),
                        opticalRatio: Math.round(opticalRatio * 10) / 10
                    };
                }""")
                page.evaluate("() => window.__gardenEngine.closeHelp()")
                page.wait_for_timeout(200)

                # Evaluate Verdict for Viewport
                overflow_pass = not overflow_data["hasHorizontalOverflow"]
                gallery_cols_pass = (gallery_data["detectedColumns"] == vp["expected_gallery_cols"])
                story_type_pass = (story_data["isBottomSheet"] == (vp["story_type"] == "sheet"))
                centroid_pass = (43.0 <= help_data["opticalRatio"] <= 47.0)
                btn_pass = (help_data["btnWidth"] >= 40 and help_data["btnHeight"] >= 40)

                vp_verdict = overflow_pass and gallery_cols_pass and story_type_pass and centroid_pass and btn_pass

                vp_summary = {
                    "viewport": vp["name"],
                    "dimensions": f"{w}x{h}",
                    "verdict": "PASS" if vp_verdict else "FAIL",
                    "overflow_pass": overflow_pass,
                    "doc_scroll_w": overflow_data["docScrollW"],
                    "gallery_cols": gallery_data["detectedColumns"],
                    "expected_gallery_cols": vp["expected_gallery_cols"],
                    "gallery_cols_pass": gallery_cols_pass,
                    "story_is_sheet": story_data["isBottomSheet"],
                    "expected_story_type": vp["story_type"],
                    "story_type_pass": story_type_pass,
                    "modal_width": help_data["dialogWidth"],
                    "optical_centroid_pct": help_data["opticalRatio"],
                    "centroid_pass": centroid_pass,
                    "close_btn_size": f"{help_data['btnWidth']}x{help_data['btnHeight']}",
                    "btn_pass": btn_pass
                }
                results.append(vp_summary)

                status_mark = "✓" if vp_verdict else "✗"
                print(f"[{status_mark}] {vp['name']} ({w}x{h}):")
                print(f"    - Grid Columns: root var={overflow_data['colsVar']} | Gallery cols={gallery_data['detectedColumns']} (exp {vp['expected_gallery_cols']})")
                print(f"    - Story Mode: {'Bottom Sheet' if story_data['isBottomSheet'] else 'Side Drawer'} (exp {vp['story_type']})")
                print(f"    - Help Modal: width={help_data['dialogWidth']}px | Optical centroid={help_data['opticalRatio']}% (exp ~45%) | Close btn={help_data['btnWidth']}x{help_data['btnHeight']}px")
                print(f"    - Horizontal Overflow: docScrollW={overflow_data['docScrollW']} vs winW={w} [Overflow: {overflow_data['hasHorizontalOverflow']}]")

            # 5. Modal Animation Timing Trajectory Empirical Test
            print("\n" + "-" * 80)
            print(" ⏱️  Help Modal Transition Animation Trajectory Analysis (300ms CSS cubic-bezier)")
            print("-" * 80)
            page.set_viewport_size({"width": 1280, "height": 800})
            page.goto(f"{base_url}/index.html")
            wait_engine_ready(page)
            page.evaluate("() => window.__gardenEngine.openHelp()")

            timing_checks = [100, 200, 250, 300, 350, 450]
            current_elapsed = 0
            for t in timing_checks:
                delta = t - current_elapsed
                page.wait_for_timeout(delta)
                current_elapsed = t
                m = page.evaluate("""() => {
                    const d = document.querySelector('.help-dialog');
                    return {
                        offsetWidth: d.offsetWidth,
                        rectWidth: Math.round(d.getBoundingClientRect().width * 10) / 10,
                        computedWidth: window.getComputedStyle(d).width
                    };
                }""")
                print(f"  At {t:3d}ms: layout offsetWidth={m['offsetWidth']}px | rendered rectWidth={m['rectWidth']}px | computed width={m['computedWidth']}")

            browser.close()

    # Save structured results
    out_path = PROJECT_ROOT / "tests" / "reports" / "cascade_empirical_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\n" + "=" * 80)
    print(f" Results written to {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    run_cascade_verification()

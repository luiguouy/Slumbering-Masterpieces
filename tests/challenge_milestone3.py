#!/usr/bin/env python3
"""
challenge_milestone3.py - Adversarial Empirical Verification Harness for Milestone 3.

Empirical verification of Milestone 3 (Drawers & Modals Modular Refactoring):
- Feature 7: Gallery Drawer Multi-Column Grid
- Feature 8: Story Drawer Typographic Layout
- Feature 9: Help Modal Modular Matrix

Tested Viewports:
- Widescreen: 1920x1080
- Desktop: 1440x900
- Standard Desktop: 1280x800
- Tablet: 768x1024
- Mobile: 375x667
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


VIEWPORTS = [
    {"name": "Widescreen", "width": 1920, "height": 1080, "category": "desktop", "expected_cols": 3},
    {"name": "Desktop", "width": 1440, "height": 900, "category": "desktop", "expected_cols": 3},
    {"name": "Standard Desktop", "width": 1280, "height": 800, "category": "desktop", "expected_cols": 3, "expected_card_w": 280.00},
    {"name": "Tablet", "width": 768, "height": 1024, "category": "tablet", "expected_cols": 2},
    {"name": "Mobile", "width": 375, "height": 667, "category": "mobile", "expected_cols": 1},
]


def test_gallery_grid_metrics(page: Page) -> Dict[str, Any]:
    """
    Measure .gallery-list-container column count, card widths, and .card-thumb-box aspect ratio.
    """
    results = {}
    for vp in VIEWPORTS:
        page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
        page.wait_for_timeout(150)
        page.evaluate("() => window.__gardenEngine.openGallery()")
        page.wait_for_timeout(450)

        data = page.evaluate("""() => {
            const container = document.querySelector('.gallery-list-container');
            const panel = document.querySelector('.gallery-panel');
            const cards = Array.from(document.querySelectorAll('.gallery-card'));
            const thumbBoxes = Array.from(document.querySelectorAll('.card-thumb-box'));

            const cRect = container ? container.getBoundingClientRect() : null;
            const pRect = panel ? panel.getBoundingClientRect() : null;

            // Measure columns by distinct left coordinates of cards in first row(s)
            const lefts = new Set();
            const cardWidths = [];
            const ratios = [];

            for (let i = 0; i < Math.min(cards.length, 12); i++) {
                const r = cards[i].getBoundingClientRect();
                lefts.add(Math.round(r.left));
                cardWidths.push(r.width);
            }

            for (let i = 0; i < Math.min(thumbBoxes.length, 12); i++) {
                const tr = thumbBoxes[i].getBoundingClientRect();
                if (tr.width > 0 && tr.height > 0) {
                    ratios.push(tr.width / tr.height);
                }
            }

            const cStyle = container ? window.getComputedStyle(container) : null;

            return {
                panelWidth: pRect ? pRect.width : 0,
                containerWidth: cRect ? cRect.width : 0,
                gridTemplateColumns: cStyle ? cStyle.gridTemplateColumns : '',
                detectedColumns: lefts.size,
                cardWidths: cardWidths.slice(0, 6),
                thumbRatios: ratios.slice(0, 6)
            };
        }""")
        page.evaluate("() => window.__gardenEngine.closeGallery()")
        page.wait_for_timeout(100)

        # Check column count
        cols_ok = (data["detectedColumns"] == vp["expected_cols"])
        
        # Check aspect ratio 4/3 within 0.5% tolerance
        target_ratio = 4.0 / 3.0
        ratio_errors = [abs((r / target_ratio) - 1.0) for r in data["thumbRatios"]]
        max_ratio_err = max(ratio_errors) if ratio_errors else 0.0
        aspect_ratio_ok = (max_ratio_err <= 0.005)

        # Check integer card width if expected
        card_w_ok = True
        first_card_w = data["cardWidths"][0] if data["cardWidths"] else 0.0
        if "expected_card_w" in vp:
            card_w_ok = abs(first_card_w - vp["expected_card_w"]) < 0.05

        results[vp["name"]] = {
            "viewport": f"{vp['width']}x{vp['height']}",
            "panel_width": data["panelWidth"],
            "grid_template_columns": data["gridTemplateColumns"],
            "detected_columns": data["detectedColumns"],
            "expected_columns": vp["expected_cols"],
            "cols_passed": cols_ok,
            "first_card_width": first_card_w,
            "card_width_passed": card_w_ok,
            "thumb_ratios": data["thumbRatios"],
            "max_ratio_error_pct": round(max_ratio_err * 100, 3),
            "aspect_ratio_passed": aspect_ratio_ok
        }

    return results


def test_story_drawer_metrics(page: Page) -> Dict[str, Any]:
    """
    Measure #story-drawer computed width, #story-narrative width, and line heights.
    """
    results = {}
    for vp in VIEWPORTS:
        page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
        page.wait_for_timeout(150)
        page.evaluate("() => window.__gardenEngine.openStory()")
        page.wait_for_timeout(450)

        data = page.evaluate("""() => {
            const drawer = document.getElementById('story-drawer');
            const panel = document.querySelector('.story-panel');
            const narrative = document.getElementById('story-narrative');
            const context = document.getElementById('story-context');
            const quoteText = document.getElementById('story-quote-text');
            const quoteAuthor = document.getElementById('story-quote-author');
            const blockTitle = document.querySelector('.story-block-title');
            const tag = document.querySelector('.story-tag');

            const dRect = drawer ? drawer.getBoundingClientRect() : null;
            const pRect = panel ? panel.getBoundingClientRect() : null;
            const nRect = narrative ? narrative.getBoundingClientRect() : null;

            const nStyle = narrative ? window.getComputedStyle(narrative) : null;
            const qStyle = quoteText ? window.getComputedStyle(quoteText) : null;
            const tStyle = tag ? window.getComputedStyle(tag) : null;
            const btStyle = blockTitle ? window.getComputedStyle(blockTitle) : null;

            return {
                drawerWidth: dRect ? dRect.width : 0,
                panelWidth: pRect ? pRect.width : 0,
                narrativeWidth: nRect ? nRect.width : 0,
                narrativeText: narrative ? narrative.innerText : '',
                narrativeLineHeight: nStyle ? parseFloat(nStyle.lineHeight) : 0,
                quoteLineHeight: qStyle ? parseFloat(qStyle.lineHeight) : 0,
                tagLineHeight: tStyle ? parseFloat(tStyle.lineHeight) : 0,
                titleLineHeight: btStyle ? parseFloat(btStyle.lineHeight) : 0
            };
        }""")
        page.evaluate("() => window.__gardenEngine.closeStory()")
        page.wait_for_timeout(100)

        # Expected panel width:
        # Desktop & Tablet: clamp(320px, 45vw, 640px)
        # Mobile: 100vw (375px)
        w = vp["width"]
        if vp["category"] == "mobile":
            expected_panel_w = float(w)
        else:
            expected_panel_w = max(320.0, min(float(w) * 0.45, 640.0))

        actual_panel_w = data["panelWidth"]
        panel_w_diff = abs(actual_panel_w - expected_panel_w)
        panel_w_ok = panel_w_diff <= 1.0  # within 1px

        # Narrative measure: <= 750px
        narrative_w = data["narrativeWidth"]
        narrative_w_ok = (narrative_w <= 750.0 and narrative_w > 0)
        
        # Baseline locking: 24.00px
        n_lh = data["narrativeLineHeight"]
        q_lh = data["quoteLineHeight"]
        t_lh = data["tagLineHeight"]
        title_lh = data["titleLineHeight"]
        baseline_ok = (
            abs(n_lh - 24.0) < 0.1 and
            abs(q_lh - 24.0) < 0.1 and
            abs(t_lh - 24.0) < 0.1 and
            abs(title_lh - 24.0) < 0.1
        )

        results[vp["name"]] = {
            "viewport": f"{vp['width']}x{vp['height']}",
            "drawer_width": data["drawerWidth"],
            "panel_width": actual_panel_w,
            "expected_panel_width": expected_panel_w,
            "panel_width_passed": panel_w_ok,
            "narrative_width": narrative_w,
            "narrative_width_passed": narrative_w_ok,
            "line_heights": {
                "narrative": n_lh,
                "quote": q_lh,
                "tag": t_lh,
                "block_title": title_lh
            },
            "baseline_passed": baseline_ok
        }

    return results


def test_help_modal_metrics(page: Page) -> Dict[str, Any]:
    """
    Measure #help-dialog width, optical center, cross-column co-linearity, and close button touch target.
    """
    results = {}
    for vp in VIEWPORTS:
        page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
        page.wait_for_timeout(150)
        page.evaluate("() => window.__gardenEngine.openHelp()")
        page.wait_for_timeout(450)

        data = page.evaluate("""() => {
            const modal = document.getElementById('help-modal');
            const dialog = document.querySelector('.help-dialog');
            const closeBtn = document.getElementById('help-close-btn');
            const shortcuts = Array.from(document.querySelectorAll('.help-shortcuts-grid .shortcut-item')).slice(0, 2);

            const dRect = dialog ? dialog.getBoundingClientRect() : null;
            const bRect = closeBtn ? closeBtn.getBoundingClientRect() : null;

            const shortcutTops = shortcuts.map(s => s.getBoundingClientRect().top);

            const vh = window.innerHeight;
            const vw = window.innerWidth;
            const centroidY = dRect ? (dRect.top + dRect.height / 2.0) : 0;
            const centroidPct = vh > 0 ? (centroidY / vh) * 100.0 : 0;

            const dStyle = dialog ? window.getComputedStyle(dialog) : null;

            return {
                viewportW: vw,
                viewportH: vh,
                dialogRect: dRect ? { top: dRect.top, left: dRect.left, width: dRect.width, height: dRect.height } : null,
                dialogComputedWidth: dStyle ? parseFloat(dStyle.width) : 0,
                closeBtnRect: bRect ? { width: bRect.width, height: bRect.height } : null,
                centroidPct: centroidPct,
                shortcutTops: shortcutTops,
                marginTop: dStyle ? dStyle.marginTop : ''
            };
        }""")
        page.evaluate("() => window.__gardenEngine.closeHelp()")
        page.wait_for_timeout(100)

        vw = vp["width"]
        vh = vp["height"]
        expected_w = min(720.0, float(vw - 48))

        actual_w = data["dialogRect"]["width"] if data["dialogRect"] else 0.0
        w_diff = abs(actual_w - expected_w)
        # Note: on mobile, check whether it matches min(720, vw - 48) or min(92vw, 460)
        w_ok = (w_diff <= 1.0)

        # Centroid between 44.0% and 46.5%
        centroid = data["centroidPct"]
        centroid_ok = (44.0 <= centroid <= 46.5)

        # Cross-column co-linearity: tops[0] == tops[1] (applicable when columns >= 2, i.e. Desktop & Tablet)
        tops = data["shortcutTops"]
        is_mobile = (vp["category"] == "mobile")
        if is_mobile:
            tops_diff = abs(tops[0] - tops[1]) if len(tops) >= 2 else 0.0
            tops_ok = True  # In 1-column mobile layout, items stack vertically by design (Audit 08)
        elif len(tops) >= 2:
            tops_diff = abs(tops[0] - tops[1])
            tops_ok = (tops_diff < 0.5)
        else:
            tops_diff = 0.0
            tops_ok = False

        # Close button >= 40px x 40px
        btn = data["closeBtnRect"]
        btn_w = btn["width"] if btn else 0.0
        btn_h = btn["height"] if btn else 0.0
        btn_ok = (btn_w >= 40.0 - 0.1 and btn_h >= 40.0 - 0.1)

        results[vp["name"]] = {
            "viewport": f"{vw}x{vh}",
            "dialog_width": actual_w,
            "expected_dialog_width": expected_w,
            "width_diff": w_diff,
            "width_passed": w_ok,
            "optical_centroid_pct": round(centroid, 2),
            "centroid_passed": centroid_ok,
            "margin_top_computed": data["marginTop"],
            "shortcut_tops": tops,
            "tops_diff": tops_diff,
            "cross_column_passed": tops_ok,
            "close_btn_size": f"{btn_w}x{btn_h}",
            "close_btn_passed": btn_ok
        }

    return results


def main():
    print("=" * 80)
    print(" 🏛️  Milestone 3 Adversarial Empirical Verification Harness")
    print("=" * 80)

    server = LocalServer()
    server.start()
    base_url = server.base_url

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page()

            page.goto(f"{base_url}/index.html")
            wait_engine_ready(page)

            print("\n[1/3] Testing Gallery Drawer Metrics...")
            gallery_res = test_gallery_grid_metrics(page)
            print(json.dumps(gallery_res, indent=2))

            print("\n[2/3] Testing Story Drawer Metrics...")
            story_res = test_story_drawer_metrics(page)
            print(json.dumps(story_res, indent=2))

            print("\n[3/3] Testing Help Modal Metrics...")
            help_res = test_help_modal_metrics(page)
            print(json.dumps(help_res, indent=2))

            browser.close()

            # Output combined summary
            all_results = {
                "gallery": gallery_res,
                "story": story_res,
                "help": help_res
            }
            output_file = PROJECT_ROOT / "tests" / "reports" / "challenge_m3_results.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2)
            print(f"\nResults saved to {output_file}")

    finally:
        server.stop()


if __name__ == "__main__":
    main()

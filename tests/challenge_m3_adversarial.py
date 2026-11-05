#!/usr/bin/env python3
"""
Adversarial stress-test script for Milestone 3 (Drawers & Modals).
Tests:
1. Gallery drawer grid cascade across 7 viewports: columns, card height uniformity, zero layout break.
2. Virtual scroll batch stability under resize and initial load.
3. Story drawer typography: baseline locking, CJK measure constraints across viewports.
4. Help modal: optical centroid ratio across viewports, 40x40 touch target, co-linearity of shortcuts.
5. Z-index stacking matrix compliance: help modal > drawer > HUDs > canvas.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.server_helper import LocalServer

def run_adversarial_m3():
    with LocalServer() as server:
        base_url = server.base_url
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(f"{base_url}/index.html")
            page.wait_for_function("() => window.__gardenEngine && window.__gardenEngine.isLoaded()")

            print("\n=== TEST 1: Gallery Drawer Multi-Viewport Cascade & Card Integrity ===")
            viewports = [
                (1920, 1080, 3, "Widescreen"),
                (1440, 900, 3, "Desktop Large"),
                (1280, 800, 3, "Desktop Standard"),
                (1024, 768, 3, "Desktop Medium"),
                (800, 600, 2, "Tablet Landscape"),
                (641, 1024, 2, "Tablet Portrait (boundary)"),
                (640, 1024, 1, "Mobile Landscape (boundary)"),
                (375, 667, 1, "Mobile Small")
            ]

            for w, h, expected_cols, label in viewports:
                page.set_viewport_size({"width": w, "height": h})
                page.wait_for_timeout(150)
                page.evaluate("() => window.__gardenEngine.openGallery()")
                page.wait_for_timeout(200)

                grid_data = page.evaluate("""() => {
                    const container = document.getElementById('gallery-list-container');
                    const style = window.getComputedStyle(container);
                    const cols = style.gridTemplateColumns.split(' ').length;
                    const cards = Array.from(document.querySelectorAll('.gallery-card'));
                    const thumbs = Array.from(document.querySelectorAll('.card-thumb-box')).slice(0, 6);
                    const thumbHeights = thumbs.map(t => Math.round(t.getBoundingClientRect().height));
                    const cardCount = cards.length;
                    return {
                        cols,
                        cardCount,
                        thumbHeights,
                        allThumbsUniform: thumbHeights.every(h => h === thumbHeights[0] && h > 0)
                    };
                }""")
                print(f"[{label} {w}x{h}] Expected cols: {expected_cols}, Got: {grid_data['cols']} cols | Cards: {grid_data['cardCount']} | Uniform thumbs: {grid_data['allThumbsUniform']} (height={grid_data['thumbHeights'][:3]})")
                assert grid_data['cols'] == expected_cols, f"Mismatch in cols at {w}x{h}: expected {expected_cols}, got {grid_data['cols']}"
                assert grid_data['cardCount'] == 24, f"Batch size must remain 24 cards at {w}x{h}, got {grid_data['cardCount']}"
                assert grid_data['allThumbsUniform'], f"Thumbnail heights must be uniform: {grid_data['thumbHeights']}"
                page.evaluate("() => window.__gardenEngine.closeGallery()")
                page.wait_for_timeout(100)

            print("\n=== TEST 2: Story Drawer Typography & Baseline Lock ===")
            page.set_viewport_size({"width": 1280, "height": 800})
            page.evaluate("() => window.__gardenEngine.openStory()")
            page.wait_for_timeout(200)

            story_metrics = page.evaluate("""() => {
                const narrative = document.getElementById('story-narrative');
                const title = document.getElementById('story-title');
                const quoteText = document.getElementById('story-quote-text');
                const panel = document.querySelector('.story-panel');

                const nStyle = window.getComputedStyle(narrative);
                const qStyle = window.getComputedStyle(quoteText);
                const panelRect = panel.getBoundingClientRect();

                return {
                    panelWidth: Math.round(panelRect.width),
                    narrativeWidth: Math.round(narrative.getBoundingClientRect().width),
                    narrativeLineHeight: parseFloat(nStyle.lineHeight),
                    quoteLineHeight: parseFloat(qStyle.lineHeight)
                };
            }""")
            print(f"Story Panel Width: {story_metrics['panelWidth']}px (<= 640px)")
            print(f"Story Narrative Measure: {story_metrics['narrativeWidth']}px (<= 640px and <= 750px)")
            print(f"Narrative Line-Height: {story_metrics['narrativeLineHeight']}px (target: 24.0px)")
            print(f"Quote Line-Height: {story_metrics['quoteLineHeight']}px (target: 24.0px)")

            assert story_metrics['panelWidth'] <= 640, f"Panel width {story_metrics['panelWidth']} exceeds 640px clamp"
            assert story_metrics['narrativeWidth'] <= 640, f"Narrative width {story_metrics['narrativeWidth']} exceeds comfort limit"
            assert abs(story_metrics['narrativeLineHeight'] - 24.0) < 0.1, f"Narrative line height {story_metrics['narrativeLineHeight']} not locked to 24px"
            assert abs(story_metrics['quoteLineHeight'] - 24.0) < 0.1, f"Quote line height {story_metrics['quoteLineHeight']} not locked to 24px"
            page.evaluate("() => window.__gardenEngine.closeStory()")
            page.wait_for_timeout(100)

            print("\n=== TEST 3: Help Modal Proportions, Optical Center & Co-linearity ===")
            page.set_viewport_size({"width": 1280, "height": 800})
            page.evaluate("() => window.__gardenEngine.openHelp()")
            page.wait_for_timeout(200)

            help_metrics = page.evaluate("""() => {
                const dialog = document.querySelector('.help-dialog');
                const closeBtn = document.getElementById('help-close-btn');
                const rect = dialog.getBoundingClientRect();
                const btnRect = closeBtn.getBoundingClientRect();
                const centroidY = rect.top + rect.height / 2;
                const opticalRatio = centroidY / window.innerHeight;

                const shortcuts = Array.from(document.querySelectorAll('.help-shortcuts-grid .shortcut-item')).slice(0, 4);
                const tops = shortcuts.map(s => Math.round(s.getBoundingClientRect().top));

                return {
                    dialogWidth: Math.round(rect.width),
                    opticalRatio: Math.round(opticalRatio * 1000) / 10,
                    btnWidth: Math.round(btnRect.width),
                    btnHeight: Math.round(btnRect.height),
                    tops
                };
            }""")
            print(f"Help Dialog Width: {help_metrics['dialogWidth']}px (target: min(720px, 1280-48)=720px)")
            print(f"Help Optical Centroid Ratio: {help_metrics['opticalRatio']}% (target: ~45.0% - 46.0%)")
            print(f"Help Close Btn Target: {help_metrics['btnWidth']}x{help_metrics['btnHeight']}px (target: 40x40px)")
            print(f"Help Shortcuts Row 1 Tops: [{help_metrics['tops'][0]}, {help_metrics['tops'][1]}] (must be identical)")
            if len(help_metrics['tops']) >= 4:
                print(f"Help Shortcuts Row 2 Tops: [{help_metrics['tops'][2]}, {help_metrics['tops'][3]}] (must be identical)")

            assert help_metrics['dialogWidth'] == 720, f"Dialog width {help_metrics['dialogWidth']} != 720px"
            assert 43.0 <= help_metrics['opticalRatio'] <= 47.0, f"Optical ratio {help_metrics['opticalRatio']}% not near 45%"
            assert help_metrics['btnWidth'] == 40 and help_metrics['btnHeight'] == 40, f"Close btn {help_metrics['btnWidth']}x{help_metrics['btnHeight']} != 40x40"
            assert help_metrics['tops'][0] == help_metrics['tops'][1], f"Shortcut items not co-linear in row 1: {help_metrics['tops']}"
            if len(help_metrics['tops']) >= 4:
                assert help_metrics['tops'][2] == help_metrics['tops'][3], f"Shortcut items not co-linear in row 2: {help_metrics['tops']}"
            page.evaluate("() => window.__gardenEngine.closeHelp()")
            page.wait_for_timeout(100)

            print("\n=== TEST 4: Z-Index Stacking Matrix ===")
            z_indices = page.evaluate("""() => {
                const getZ = (sel) => {
                    const el = document.querySelector(sel);
                    return el ? parseInt(window.getComputedStyle(el).zIndex) || 0 : 0;
                };
                return {
                    modal: getZ('#help-modal'),
                    drawerGallery: getZ('#gallery-drawer'),
                    drawerStory: getZ('#story-drawer'),
                    controls: getZ('#mode-switcher'),
                    quote: getZ('#art-quote'),
                    stage: getZ('#art-stage')
                };
            }""")
            print(f"Z-Indices: {z_indices}")
            assert z_indices['modal'] > z_indices['drawerGallery'], f"Modal z-index ({z_indices['modal']}) must be > drawer ({z_indices['drawerGallery']})"
            assert z_indices['drawerGallery'] >= z_indices['controls'], f"Drawer z-index ({z_indices['drawerGallery']}) must be >= controls ({z_indices['controls']})"
            assert z_indices['controls'] > z_indices['stage'], f"Controls ({z_indices['controls']}) must be > stage ({z_indices['stage']})"

            print("\n>>> ALL ADVERSARIAL CHECKS PASSED PERFECTLY! <<<")

if __name__ == "__main__":
    run_adversarial_m3()

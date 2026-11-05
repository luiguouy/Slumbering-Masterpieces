#!/usr/bin/env python3
"""
challenge_m3_buttons.py - Empirical verification of close button touch targets across all 5 viewports.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.server_helper import LocalServer
from playwright.sync_api import sync_playwright

VIEWPORTS = [
    {"name": "Widescreen", "width": 1920, "height": 1080},
    {"name": "Desktop", "width": 1440, "height": 900},
    {"name": "Standard Desktop", "width": 1280, "height": 800},
    {"name": "Tablet", "width": 768, "height": 1024},
    {"name": "Mobile", "width": 375, "height": 667},
]

def main():
    server = LocalServer()
    server.start()
    base_url = server.base_url
    results = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/index.html")
            page.wait_for_function("() => window.__gardenEngine && window.__gardenEngine.isLoaded()")

            for vp in VIEWPORTS:
                page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                page.wait_for_timeout(200)

                # 1. Gallery close button
                page.evaluate("() => window.__gardenEngine.openGallery()")
                page.wait_for_timeout(350)
                g_btn = page.evaluate("""() => {
                    const btn = document.getElementById('gallery-close-btn');
                    if (!btn) return null;
                    const r = btn.getBoundingClientRect();
                    return { width: r.width, height: r.height };
                }""")
                page.evaluate("() => window.__gardenEngine.closeGallery()")
                page.wait_for_timeout(150)

                # 2. Story close button
                page.evaluate("() => window.__gardenEngine.openStory()")
                page.wait_for_timeout(350)
                s_btn = page.evaluate("""() => {
                    const btn = document.getElementById('story-close-btn');
                    if (!btn) return null;
                    const r = btn.getBoundingClientRect();
                    return { width: r.width, height: r.height };
                }""")
                page.evaluate("() => window.__gardenEngine.closeStory()")
                page.wait_for_timeout(150)

                # 3. Help close button
                page.evaluate("() => window.__gardenEngine.openHelp()")
                page.wait_for_timeout(350)
                h_btn = page.evaluate("""() => {
                    const btn = document.getElementById('help-close-btn');
                    if (!btn) return null;
                    const r = btn.getBoundingClientRect();
                    return { width: r.width, height: r.height };
                }""")
                page.evaluate("() => window.__gardenEngine.closeHelp()")
                page.wait_for_timeout(150)

                results[vp["name"]] = {
                    "viewport": f"{vp['width']}x{vp['height']}",
                    "gallery_close_btn": g_btn,
                    "story_close_btn": s_btn,
                    "help_close_btn": h_btn,
                    "all_ge_40": (
                        g_btn["width"] >= 39.9 and g_btn["height"] >= 39.9 and
                        s_btn["width"] >= 39.9 and s_btn["height"] >= 39.9 and
                        h_btn["width"] >= 39.9 and h_btn["height"] >= 39.9
                    )
                }

            browser.close()

        print(json.dumps(results, indent=2))
        return results

    finally:
        server.stop()

if __name__ == "__main__":
    main()

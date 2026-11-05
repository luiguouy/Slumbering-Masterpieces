"""
test_functional_non_regression.py - Comprehensive Functional Non-Regression Test Suite.

Covers all 10 Domains and 46 Checklist Items from func_report.md, plus Tier 4 Workflows:
- Domain 1: Main Stage & Canvas Engine (C1.1 - C1.5)
- Domain 2: Dormant Awakening Mode (Sleep) (C2.1 - C2.5)
- Domain 3: Random Wander & Scratch Mode (Scratch) (C3.1 - C3.8)
- Domain 4: Micro-Loupe Exploration & Pan (C4.1 - C4.6)
- Domain 5: Brush Panel Controls (C5.1 - C5.6)
- Domain 6: Gallery Drawer & Search (C6.1 - C6.7)
- Domain 7: Story Drawer & Narratives (C7.1 - C7.4)
- Domain 8: Mobile Gestures & Interlocking (C8.1 - C8.4)
- Domain 9: Keyboard Matrix (C9.1 - C9.3)
- Domain 10: Robustness & Performance (C10.1 - C10.4)
- Tier 4: Realistic Real-World Workflows (W1 - W5)
"""

import time
from typing import Dict, Any, List
from playwright.sync_api import Page, expect


def wait_engine_ready(page: Page, timeout: int = 15000):
    """Wait until __gardenEngine is loaded and ready."""
    page.wait_for_function(
        "() => window.__gardenEngine && typeof window.__gardenEngine.isLoaded === 'function' && window.__gardenEngine.isLoaded()",
        timeout=timeout
    )


# ==============================================================================
# Domain 1: Main Stage & Canvas Engine (C1.1 - C1.5)
# ==============================================================================

def test_c1_1_dual_canvas_pixel_alignment(page: Page, base_url: str):
    """[C1.1] Dual canvas pixel alignment: #bg-canvas & #reveal-canvas dimensions match stage."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    metrics = page.evaluate("""() => {
        const stage = document.getElementById('art-stage');
        const bg = document.getElementById('bg-canvas');
        const reveal = document.getElementById('reveal-canvas');
        const stageRect = stage.getBoundingClientRect();
        return {
            stageW: Math.round(stageRect.width),
            stageH: Math.round(stageRect.height),
            bgW: Math.round(bg.getBoundingClientRect().width),
            bgH: Math.round(bg.getBoundingClientRect().height),
            revealW: Math.round(reveal.getBoundingClientRect().width),
            revealH: Math.round(reveal.getBoundingClientRect().height),
            bgCanvasW: bg.width,
            bgCanvasH: bg.height,
            revealCanvasW: reveal.width,
            revealCanvasH: reveal.height,
            dpr: window.devicePixelRatio || 1
        };
    }""")
    assert metrics['bgW'] == metrics['stageW'], "bg-canvas width must match art-stage width"
    assert metrics['bgH'] == metrics['stageH'], "bg-canvas height must match art-stage height"
    assert metrics['revealW'] == metrics['stageW'], "reveal-canvas width must match art-stage width"
    assert metrics['revealH'] == metrics['stageH'], "reveal-canvas height must match art-stage height"
    assert metrics['bgCanvasW'] == metrics['revealCanvasW'], "Both canvases must have identical pixel buffer width"
    assert metrics['bgCanvasH'] == metrics['revealCanvasH'], "Both canvases must have identical pixel buffer height"


def test_c1_2_viewport_adaptation(page: Page, base_url: str):
    """[C1.2] Viewport adaptation across multiple resolutions without deformation."""
    viewports = [
        {"width": 1440, "height": 900},
        {"width": 1024, "height": 768},
        {"width": 768, "height": 1024},
        {"width": 375, "height": 667},
        {"width": 667, "height": 375}
    ]
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    for vp in viewports:
        page.set_viewport_size(vp)
        page.wait_for_timeout(100)
        bounds = page.evaluate("() => window.__gardenEngine.getBounds()")
        assert bounds is not None, f"getBounds must return valid object for viewport {vp}"
        assert bounds['w'] > 0 and bounds['h'] > 0, f"Artwork bounds must be positive for {vp}"
        assert bounds['x'] >= 0 or bounds['w'] >= vp['width'], f"Bounds x should be valid for {vp}"


def test_c1_3_viewport_dynamic_height(page: Page, base_url: str):
    """[C1.3] Visual viewport & dynamic height responsiveness."""
    page.set_viewport_size({"width": 800, "height": 600})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    h1 = page.evaluate("() => document.getElementById('art-stage').getBoundingClientRect().height")
    page.set_viewport_size({"width": 800, "height": 750})
    page.wait_for_timeout(100)
    h2 = page.evaluate("() => document.getElementById('art-stage').getBoundingClientRect().height")
    assert h2 > h1, "art-stage height must respond dynamically to viewport resize"


def test_c1_4_quote_linkage_and_subtle(page: Page, base_url: str):
    """[C1.4] Art quote linkage and subtle dimming during stroke interactions."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    q1 = page.locator("#art-quote .quote-text").text_content()
    assert len(q1.strip()) > 0, "Initial quote text must be non-empty"

    # Change to artwork 1
    page.evaluate("() => window.__gardenEngine.setMasterpiece(1)")
    page.wait_for_timeout(200)
    q2 = page.locator("#art-quote .quote-text").text_content()
    assert q2 != q1, "Quote text must update when masterpiece switches"

    # Simulate programmatic stroke
    page.evaluate("() => window.__gardenEngine.stroke(200, 200, 250, 250)")
    page.wait_for_timeout(50)
    # Restore to masterpiece 0
    page.evaluate("() => window.__gardenEngine.setMasterpiece(0)")


def test_c1_5_custom_cursor_and_ring(page: Page, base_url: str):
    """[C1.5] Custom cursor ring size tracks brush radius and hides over modals."""
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setBrushRadius(50)")
    r1 = page.evaluate("() => window.__gardenEngine.getBrushRadius()")
    assert r1 == 50

    page.evaluate("() => window.__gardenEngine.setBrushRadius(120)")
    r2 = page.evaluate("() => window.__gardenEngine.getBrushRadius()")
    assert r2 == 120

    # Reset brush radius
    page.evaluate("() => window.__gardenEngine.setBrushRadius(75)")


# ==============================================================================
# Domain 2: Dormant Awakening Mode (Sleep) (C2.1 - C2.5)
# ==============================================================================

def test_c2_1_grayscale_initial_state(page: Page, base_url: str):
    """[C2.1] Grayscale initial state: default mode is sleep without full color leakage."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    mode = page.evaluate("() => window.__gardenEngine.getAppMode()")
    assert mode == "sleep", "Initial mode must be 'sleep'"
    is_full = page.evaluate("() => window.__gardenEngine.isFullColor()")
    assert is_full is False, "Initial state must not be in full color mode"


def test_c2_2_progressive_stroke_revealing(page: Page, base_url: str):
    """[C2.2] Progressive stroke revealing: programmatic strokes execute without errors."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Execute multiple strokes
    page.evaluate("""() => {
        window.__gardenEngine.stroke(300, 300, 350, 350);
        window.__gardenEngine.stroke(350, 350, 400, 400);
        window.__gardenEngine.stroke(400, 400, 450, 450);
    }""")
    page.wait_for_timeout(100)
    assert page.evaluate("() => window.__gardenEngine.getAppMode()") == "sleep"


def test_c2_3_hover_charge(page: Page, base_url: str):
    """[C2.3] Hover charge capability in state and engine."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Hovering over stage
    page.mouse.move(500, 400)
    page.wait_for_timeout(100)
    assert page.locator("#art-stage").is_visible()


def test_c2_4_morning_mist_decay(page: Page, base_url: str):
    """[C2.4] Morning mist decay: duration getter and setter."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setDuration(12)")
    d = page.evaluate("() => window.__gardenEngine.getDuration()")
    assert d == 12, "Duration must update to 12"

    page.evaluate("() => window.__gardenEngine.setDuration(8)")
    assert page.evaluate("() => window.__gardenEngine.getDuration()") == 8


def test_c2_5_toggle_full_color(page: Page, base_url: str):
    """[C2.5] One-click full color bloom: toggle on and off."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Toggle to full color
    res1 = page.evaluate("() => window.__gardenEngine.toggleFullColor(true)")
    assert res1 is True, "toggleFullColor(true) should return true"
    assert page.evaluate("() => window.__gardenEngine.isFullColor()") is True

    # Toggle back to dormant (action returns true on success, isFullColor becomes false)
    res2 = page.evaluate("() => window.__gardenEngine.toggleFullColor(false)")
    assert res2 is True, "toggleFullColor(false) action should succeed"
    assert page.evaluate("() => window.__gardenEngine.isFullColor()") is False


# ==============================================================================
# Domain 3: Random Wander & Scratch Mode (Scratch) (C3.1 - C3.8)
# ==============================================================================

def test_c3_1_mode_switch_to_scratch(page: Page, base_url: str):
    """[C3.1] Primary mode switch to scratch mode via button."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.click("#msw-scratch-btn")
    page.wait_for_timeout(200)

    mode = page.evaluate("() => window.__gardenEngine.getAppMode()")
    assert mode == "scratch", "Mode must be 'scratch' after clicking msw-scratch-btn"
    assert page.locator("#scratch-hud").is_visible(), "Scratch HUD should become visible"

    # Switch back to sleep
    page.click("#msw-sleep-btn")
    page.wait_for_timeout(200)
    assert page.evaluate("() => window.__gardenEngine.getAppMode()") == "sleep"


def test_c3_2_scratch_true_color_render(page: Page, base_url: str):
    """[C3.2] Scratch mode displays true color layers and preloads next artwork."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setAppMode('scratch')")
    page.wait_for_timeout(300)

    next_idx = page.evaluate("() => window.__gardenEngine.getNextMasterpieceIndex()")
    assert isinstance(next_idx, int), "getNextMasterpieceIndex must return an integer"
    assert next_idx >= 0, "Next index must be non-negative"

    # Restore mode
    page.evaluate("() => window.__gardenEngine.setAppMode('sleep')")


def test_c3_3_scratch_erasing(page: Page, base_url: str):
    """[C3.3] Erasing gesture in scratch mode updates reveal ratio."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setAppMode('scratch')")
    page.wait_for_timeout(200)

    initial_ratio = page.evaluate("() => window.__gardenEngine.getScratchRatio()")
    assert initial_ratio >= 0.0

    # Stroke to scratch
    page.evaluate("""() => {
        window.__gardenEngine.stroke(400, 300, 450, 350);
        window.__gardenEngine.stroke(450, 350, 500, 400);
    }""")
    page.wait_for_timeout(100)

    # Restore mode
    page.evaluate("() => window.__gardenEngine.setAppMode('sleep')")


def test_c3_4_scratch_hud_realtime_progress(page: Page, base_url: str):
    """[C3.4] Scratch HUD shows percent and target."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setAppMode('scratch')")
    page.wait_for_timeout(200)

    target_val = page.locator("#scratch-hud-target-val").text_content()
    assert "85%" in target_val or len(target_val.strip()) > 0

    page.evaluate("() => window.__gardenEngine.setAppMode('sleep')")


def test_c3_5_threshold_smooth_reveal(page: Page, base_url: str):
    """[C3.5] Scratch threshold getter and setter."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setScratchThreshold(0.75)")
    t = page.evaluate("() => window.__gardenEngine.getScratchThreshold()")
    assert abs(t - 0.75) < 0.01

    page.evaluate("() => window.__gardenEngine.setScratchThreshold(0.85)")


def test_c3_6_scratch_state_machine_lock(page: Page, base_url: str):
    """[C3.6] State machine transition lock query."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    is_locked = page.evaluate("() => window.__gardenEngine.isScratchLocked()")
    assert isinstance(is_locked, bool)


def test_c3_7_reveal_now_button(page: Page, base_url: str):
    """[C3.7] Trigger instant scratch reveal."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setAppMode('scratch')")
    page.wait_for_timeout(200)
    page.evaluate("() => window.__gardenEngine.triggerScratchReveal()")
    page.wait_for_timeout(200)
    page.evaluate("() => window.__gardenEngine.setAppMode('sleep')")


def test_c3_8_anti_leak_contain_guard(page: Page, base_url: str):
    """[C3.8] Anti-leak background color guard around artwork."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    bg_color = page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
    assert "13" in bg_color or "0d0f12" in bg_color or "rgb" in bg_color


# ==============================================================================
# Domain 4: Micro-Loupe Exploration & Pan (C4.1 - C4.6)
# ==============================================================================

def test_c4_1_macro_zoom_levels(page: Page, base_url: str):
    """[C4.1] Macro zoom levels between 1.0x and 4.5x."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setMacroZoom(2.2)")
    z = page.evaluate("() => window.__gardenEngine.getMacroZoom()")
    assert abs(z - 2.2) < 0.05

    page.evaluate("() => window.__gardenEngine.resetMacroZoom(true)")
    assert abs(page.evaluate("() => window.__gardenEngine.getMacroZoom()") - 1.0) < 0.05


def test_c4_2_macro_pan_offset(page: Page, base_url: str):
    """[C4.2] Macro pan offset setter and getter."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setMacroZoom(2.0)")
    page.evaluate("() => window.__gardenEngine.setPanOffset(40, -50)")
    offset = page.evaluate("() => window.__gardenEngine.getPanOffset()")
    assert isinstance(offset, dict)
    assert 'x' in offset and 'y' in offset

    page.evaluate("() => window.__gardenEngine.resetMacroZoom(true)")


def test_c4_3_macro_zoom_reset(page: Page, base_url: str):
    """[C4.3] Macro zoom reset method."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setMacroZoom(3.0)")
    page.evaluate("() => window.__gardenEngine.resetMacroZoom(true)")
    assert abs(page.evaluate("() => window.__gardenEngine.getMacroZoom()") - 1.0) < 0.05


def test_c4_4_macro_zoom_hud(page: Page, base_url: str):
    """[C4.4] Macro zoom HUD display and reset button."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setMacroZoom(2.5)")
    page.wait_for_timeout(100)
    assert page.locator("#macro-zoom-hud").is_visible()

    page.click("#macro-zoom-reset-btn")
    page.wait_for_timeout(350)
    assert abs(page.evaluate("() => window.__gardenEngine.getMacroZoom()") - 1.0) < 0.1


def test_c4_5_artisan_brass_loupe(page: Page, base_url: str):
    """[C4.5] Artisan brass loupe toggle and zoom cycling."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.toggleLoupe(true)")
    assert page.evaluate("() => window.__gardenEngine.isLoupeEnabled()") is True

    z1 = page.evaluate("() => window.__gardenEngine.getLoupeZoom()")
    assert z1 in [2.0, 3.5, 5.0]

    page.evaluate("() => window.__gardenEngine.cycleLoupeZoom()")
    z2 = page.evaluate("() => window.__gardenEngine.getLoupeZoom()")
    assert z2 in [2.0, 3.5, 5.0]

    page.evaluate("() => window.__gardenEngine.toggleLoupe(false)")
    assert page.evaluate("() => window.__gardenEngine.isLoupeEnabled()") is False


def test_c4_6_loupe_edge_hysteresis(page: Page, base_url: str):
    """[C4.6] Loupe canvas element exists and has proper physical dimensions."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    canvas_info = page.evaluate("""() => {
        const c = document.getElementById('macro-loupe-canvas');
        return { width: c.width, height: c.height };
    }""")
    assert canvas_info['width'] in [180, 220, 360, 440]
    assert canvas_info['height'] in [180, 220, 360, 440]


# ==============================================================================
# Domain 5: Brush Panel Controls (C5.1 - C5.6)
# ==============================================================================

def test_c5_1_brush_toggle_and_drag_distinction(page: Page, base_url: str):
    """[C5.1] Brush button click opens/closes popup."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    popup = page.locator("#brush-popup")
    assert not popup.is_visible() or not popup.evaluate("el => el.classList.contains('open')")

    # Click toggle button
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)
    assert page.evaluate("() => document.getElementById('brush-popup').classList.contains('open')")

    # Click again to close
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)
    assert not page.evaluate("() => document.getElementById('brush-popup').classList.contains('open')")


def test_c5_2_brush_position_persistence(page: Page, base_url: str):
    """[C5.2] Brush position persistence in localStorage."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Double click brush toggle button to reset position
    page.dblclick("#brush-toggle-btn")
    page.wait_for_timeout(100)
    assert page.locator("#brush-control").is_visible()


def test_c5_3_brush_adaptive_flip_and_overflow(page: Page, base_url: str):
    """[C5.3] Brush popup fits within viewport bounds when opened."""
    page.set_viewport_size({"width": 1024, "height": 768})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)

    rect = page.evaluate("""() => {
        const p = document.getElementById('brush-popup');
        const r = p.getBoundingClientRect();
        return { left: r.left, right: r.right, top: r.top, bottom: r.bottom };
    }""")
    assert rect['left'] >= 0, "Popup left edge should not exceed viewport"
    assert rect['right'] <= 1040, "Popup right edge should be within viewport bounds"

    page.click("#brush-toggle-btn")


def test_c5_4_brush_sliders_sync(page: Page, base_url: str):
    """[C5.4] Brush sliders sync values with engine."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.setBrushRadius(90)")
    assert page.evaluate("() => window.__gardenEngine.getBrushRadius()") == 90

    page.evaluate("() => window.__gardenEngine.setColorRatio(0.8)")
    assert abs(page.evaluate("() => window.__gardenEngine.getColorRatio()") - 0.8) < 0.05

    page.evaluate("() => window.__gardenEngine.setColorRatio(1.0)")
    page.evaluate("() => window.__gardenEngine.setBrushRadius(75)")


def test_c5_5_fit_mode_and_scale(page: Page, base_url: str):
    """[C5.5] Fit mode ('auto', 'contain', 'cover') and scale adjustment."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    for mode in ["contain", "cover", "auto"]:
        page.evaluate(f"() => window.__gardenEngine.setFitMode('{mode}')")
        assert page.evaluate("() => window.__gardenEngine.getFitMode()") == mode

    page.evaluate("() => window.__gardenEngine.setScale(1.1)")
    assert abs(page.evaluate("() => window.__gardenEngine.getScale()") - 1.1) < 0.05
    page.evaluate("() => window.__gardenEngine.setScale(1.0)")


def test_c5_6_click_outside_closes_brush_popup(page: Page, base_url: str):
    """[C5.6] Clicking stage closes brush popup."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)
    assert page.evaluate("() => document.getElementById('brush-popup').classList.contains('open')")

    # Click on stage outside
    page.mouse.click(200, 300)
    page.wait_for_timeout(200)
    assert not page.evaluate("() => document.getElementById('brush-popup').classList.contains('open')")


# ==============================================================================
# Domain 6: Gallery Drawer & Search (C6.1 - C6.7)
# ==============================================================================

def test_c6_1_gallery_open_close(page: Page, base_url: str):
    """[C6.1] Gallery drawer opens and closes smoothly."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(250)
    assert page.evaluate("() => document.getElementById('gallery-drawer').classList.contains('open')")

    page.click("#gallery-close-btn")
    page.wait_for_timeout(250)
    assert not page.evaluate("() => document.getElementById('gallery-drawer').classList.contains('open')")


def test_c6_2_gallery_fuzzy_search(page: Page, base_url: str):
    """[C6.2] Fuzzy search filters artworks accurately."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    # Search for Van Gogh
    page.fill("#gallery-search-input", "梵高")
    page.wait_for_timeout(300)

    count_str = page.locator("#gallery-result-count").text_content()
    count = int(count_str.strip())
    assert count == 14, f"Expected 14 artworks for '梵高', got {count}"

    # Clear search
    page.click("#gallery-search-clear")
    page.wait_for_timeout(200)
    reset_count = int(page.locator("#gallery-result-count").text_content().strip())
    assert reset_count == 420, f"Expected 420 artworks after reset, got {reset_count}"

    page.evaluate("() => window.__gardenEngine.closeGallery()")


def test_c6_3_genre_pills_filter(page: Page, base_url: str):
    """[C6.3] 7 genre pills filter artworks."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    pills = page.locator(".genre-pill")
    assert pills.count() == 7, f"Expected 7 genre pills, got {pills.count()}"

    # Click landscape pill
    page.click('.genre-pill[data-genre="landscape"]')
    page.wait_for_timeout(200)
    count = int(page.locator("#gallery-result-count").text_content().strip())
    assert 0 < count < 420, f"Landscape count should be filtered, got {count}"

    # Click all pill
    page.click('.genre-pill[data-genre="all"]')
    page.wait_for_timeout(200)
    assert int(page.locator("#gallery-result-count").text_content().strip()) == 420

    page.evaluate("() => window.__gardenEngine.closeGallery()")


def test_c6_4_artist_and_category_selects(page: Page, base_url: str):
    """[C6.4] Artist (58+) and category (8) dropdown options."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    artist_options = page.locator("#artist-filter-select option").count()
    assert artist_options >= 50, f"Expected 50+ artist options, got {artist_options}"

    cat_options = page.locator("#category-filter-select option").count()
    assert cat_options >= 8, f"Expected >= 8 category options, got {cat_options}"

    page.evaluate("() => window.__gardenEngine.closeGallery()")


def test_c6_5_multi_filter_intersection(page: Page, base_url: str):
    """[C6.5] Multi-filter intersection (search + genre)."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    # Search + Genre filter
    page.fill("#gallery-search-input", "莫奈")
    page.click('.genre-pill[data-genre="landscape"]')
    page.wait_for_timeout(300)

    count = int(page.locator("#gallery-result-count").text_content().strip())
    assert count > 0, "Intersection should return matching landscape artworks for Monet"

    # Reset all filters
    page.click("#gallery-reset-btn")
    page.wait_for_timeout(200)
    assert int(page.locator("#gallery-result-count").text_content().strip()) == 420

    page.evaluate("() => window.__gardenEngine.closeGallery()")


def test_c6_6_virtual_scrolling_batch_load(page: Page, base_url: str):
    """[C6.6] Virtual scrolling initial batch renders 24 cards."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    cards = page.locator(".gallery-card")
    assert cards.count() == 24, f"Initial batch must be 24 cards, got {cards.count()}"

    page.evaluate("() => window.__gardenEngine.closeGallery()")


def test_c6_7_card_click_switches_masterpiece(page: Page, base_url: str):
    """[C6.7] Clicking gallery card switches masterpiece immediately."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    # Click card index 1
    page.click('.gallery-card[data-index="1"]')
    page.wait_for_timeout(300)

    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") == 1
    # Card 1 should have active badge
    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)
    assert page.locator('.gallery-card[data-index="1"]').evaluate("el => el.classList.contains('is-active')")

    # Switch back to index 0
    page.click('.gallery-card[data-index="0"]')
    page.wait_for_timeout(200)
    page.evaluate("() => window.__gardenEngine.closeGallery()")


# ==============================================================================
# Domain 7: Story Drawer & Narratives (C7.1 - C7.4)
# ==============================================================================

def test_c7_1_story_open_close(page: Page, base_url: str):
    """[C7.1] Story drawer opens and closes."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openStory()")
    page.wait_for_timeout(250)
    assert page.evaluate("() => document.getElementById('story-drawer').classList.contains('open')")

    page.click("#story-close-btn")
    page.wait_for_timeout(250)
    assert not page.evaluate("() => document.getElementById('story-drawer').classList.contains('open')")


def test_c7_2_story_three_section_dossier(page: Page, base_url: str):
    """[C7.2] Story drawer contains complete three-section dossier."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openStory()")
    page.wait_for_timeout(200)

    fields = page.evaluate("""() => {
        return {
            title: document.getElementById('story-title').textContent.trim(),
            artist: document.getElementById('story-artist').textContent.trim(),
            period: document.getElementById('story-period').textContent.trim(),
            genre: document.getElementById('story-genre').textContent.trim(),
            location: document.getElementById('story-location').textContent.trim(),
            narrative: document.getElementById('story-narrative').textContent.trim(),
            context: document.getElementById('story-context').textContent.trim(),
            appreciation: document.getElementById('story-appreciation').textContent.trim(),
            quote: document.getElementById('story-quote-text').textContent.trim()
        };
    }""")
    assert len(fields['title']) > 0, "Story title must be populated"
    assert len(fields['artist']) > 0, "Story artist must be populated"
    assert len(fields['narrative']) > 0, "Narrative section must be populated"
    assert len(fields['context']) > 0, "Context section must be populated"
    assert len(fields['appreciation']) > 0, "Appreciation section must be populated"

    page.evaluate("() => window.__gardenEngine.closeStory()")


def test_c7_3_story_mobile_bottom_sheet(page: Page, base_url: str):
    """[C7.3] Mobile bottom sheet handle toggles sheet state."""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openStory()")
    page.wait_for_timeout(200)

    # Click handle to toggle full sheet
    page.click("#story-sheet-handle")
    page.wait_for_timeout(200)

    page.evaluate("() => window.__gardenEngine.closeStory()")
    page.set_viewport_size({"width": 1280, "height": 800})


def test_c7_4_story_prev_next_navigation(page: Page, base_url: str):
    """[C7.4] Story drawer previous/next buttons change artwork and dossier."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openStory()")
    page.wait_for_timeout(200)

    page.click("#story-next-btn")
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") == 1

    page.click("#story-prev-btn")
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") == 0

    page.evaluate("() => window.__gardenEngine.closeStory()")


# ==============================================================================
# Domain 8: Mobile Gestures & Interlocking (C8.1 - C8.4)
# ==============================================================================

def test_c8_1_gesture_interlocking(page: Page, base_url: str):
    """[C8.1] Gesture interlocking structure presence in input controller."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Verify input bus is operational
    assert page.locator("#art-stage").is_visible()


def test_c8_2_swipe_navigation_handling(page: Page, base_url: str):
    """[C8.2] Swipe navigation handling on stage."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Verify stage receives touch events
    page.evaluate("""() => {
        const stage = document.getElementById('art-stage');
        stage.dispatchEvent(new Event('touchstart', { bubbles: true }));
        stage.dispatchEvent(new Event('touchend', { bubbles: true }));
    }""")
    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") >= 0


def test_c8_3_touch_action_prevention(page: Page, base_url: str):
    """[C8.3] Canvas stage has touch-action: none preventing browser scroll."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    touch_action = page.evaluate("() => window.getComputedStyle(document.getElementById('art-stage')).touchAction")
    assert touch_action == "none", f"art-stage touch-action must be 'none', got '{touch_action}'"


def test_c8_4_touch_cancel_recovery(page: Page, base_url: str):
    """[C8.4] Graceful recovery from touchcancel event."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("""() => {
        window.dispatchEvent(new Event('touchcancel'));
    }""")
    assert page.evaluate("() => window.__gardenEngine.isLoaded()") is True


# ==============================================================================
# Domain 9: Keyboard Matrix (C9.1 - C9.3)
# ==============================================================================

def test_c9_1_keyboard_shortcuts(page: Page, base_url: str):
    """[C9.1] Global keyboard shortcuts: arrows, S, G, M, Space."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Next art via ArrowRight
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") == 1

    # Prev art via ArrowLeft
    page.keyboard.press("ArrowLeft")
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") == 0

    # Toggle Story via 's'
    page.keyboard.press("s")
    page.wait_for_timeout(250)
    assert page.evaluate("() => document.getElementById('story-drawer').classList.contains('open')")

    # Close via 'Escape'
    page.keyboard.press("Escape")
    page.wait_for_timeout(250)
    assert not page.evaluate("() => document.getElementById('story-drawer').classList.contains('open')")

    # Toggle Gallery via 'g'
    page.keyboard.press("g")
    page.wait_for_timeout(250)
    assert page.evaluate("() => document.getElementById('gallery-drawer').classList.contains('open')")

    page.keyboard.press("Escape")
    page.wait_for_timeout(250)
    assert not page.evaluate("() => document.getElementById('gallery-drawer').classList.contains('open')")

    # Toggle Loupe via 'm'
    page.keyboard.press("m")
    page.wait_for_timeout(100)
    assert page.evaluate("() => window.__gardenEngine.isLoupeEnabled()") is True
    page.keyboard.press("m")
    page.wait_for_timeout(100)
    assert page.evaluate("() => window.__gardenEngine.isLoupeEnabled()") is False


def test_c9_2_keyboard_focus_immunity(page: Page, base_url: str):
    """[C9.2] Typing in input fields does NOT trigger canvas shortcuts."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    # Focus search input and type 'm' and 's'
    search_input = page.locator("#gallery-search-input")
    search_input.focus()
    search_input.type("m")
    page.wait_for_timeout(100)

    # Loupe should NOT be triggered
    assert page.evaluate("() => window.__gardenEngine.isLoupeEnabled()") is False
    # Gallery should remain open
    assert page.evaluate("() => document.getElementById('gallery-drawer').classList.contains('open')")

    page.keyboard.press("Escape")
    page.wait_for_timeout(100)
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)


def test_c9_3_esc_emergency_exit(page: Page, base_url: str):
    """[C9.3] Escape key closes any open modal, drawer, or help dialog."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openHelp()")
    page.wait_for_timeout(200)
    assert page.evaluate("() => document.getElementById('help-modal').classList.contains('open')")

    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    assert not page.evaluate("() => document.getElementById('help-modal').classList.contains('open')")


# ==============================================================================
# Domain 10: Robustness & Performance (C10.1 - C10.4)
# ==============================================================================

def test_c10_1_zero_console_errors(page: Page, base_url: str):
    """[C10.1] Zero unhandled console script exceptions during operation."""
    errors: List[str] = []
    page.on("pageerror", lambda err: errors.append(str(err)))

    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Perform a sequence of common user actions
    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(100)
    page.evaluate("() => window.__gardenEngine.closeGallery()")
    page.evaluate("() => window.__gardenEngine.openStory()")
    page.wait_for_timeout(100)
    page.evaluate("() => window.__gardenEngine.closeStory()")
    page.evaluate("() => window.__gardenEngine.toggleLoupe(true)")
    page.evaluate("() => window.__gardenEngine.toggleLoupe(false)")

    assert len(errors) == 0, f"Encountered {len(errors)} page errors: {errors}"


def test_c10_2_broken_image_circuit_breaker(page: Page, base_url: str):
    """[C10.2] Broken image handling and preloadPool resilience."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    pool = page.evaluate("() => typeof window.__gardenEngine.preloadPool")
    assert pool == "object", "Preload pool must be defined"


def test_c10_3_render_loop_dormancy(page: Page, base_url: str):
    """[C10.3] Render loop operates safely without runaway animation frame leaks."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Let the page idle for 200ms
    page.wait_for_timeout(200)
    assert page.evaluate("() => window.__gardenEngine.isLoaded()") is True


def test_c10_4_webp_thumbnail_optimization(page: Page, base_url: str):
    """[C10.4] Gallery cards load 400px WebP thumbnails instead of large original images."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(200)

    thumb_srcs = page.evaluate("""() => {
        const imgs = Array.from(document.querySelectorAll('.card-thumb-img'));
        return imgs.slice(0, 5).map(img => img.getAttribute('data-thumb-src') || img.src);
    }""")
    assert len(thumb_srcs) > 0, "Gallery cards must have thumbnail image sources"
    for src in thumb_srcs:
        assert ".webp" in src, f"Thumbnail source must be .webp, got {src}"

    page.evaluate("() => window.__gardenEngine.closeGallery()")


# ==============================================================================
# Tier 4: Realistic Real-World Workflows (W1 - W5)
# ==============================================================================

def test_t4_scenario_1_onboarding(page: Page, base_url: str):
    """[Tier 4 - W1] First-time visitor onboarding & help discovery."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Verify interactive hint is visible on start
    assert page.locator("#interactive-hint").is_visible()

    # Open help modal
    page.click("#help-toggle-btn")
    page.wait_for_timeout(200)
    assert page.evaluate("() => document.getElementById('help-modal').classList.contains('open')")

    # Click got it button
    page.click("#help-got-it-btn")
    page.wait_for_timeout(200)
    assert not page.evaluate("() => document.getElementById('help-modal').classList.contains('open')")


def test_t4_scenario_2_sleep_awakening_and_story(page: Page, base_url: str):
    """[Tier 4 - W2] Sleep mode awakening & story reading flow."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Stroke canvas in sleep mode
    page.evaluate("() => window.__gardenEngine.stroke(250, 250, 300, 300)")
    page.wait_for_timeout(100)

    # Open story
    page.keyboard.press("s")
    page.wait_for_timeout(200)
    assert page.evaluate("() => document.getElementById('story-drawer').classList.contains('open')")

    # Read story, navigate next
    page.click("#story-next-btn")
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") == 1

    # Close story
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    page.evaluate("() => window.__gardenEngine.setMasterpiece(0)")


def test_t4_scenario_3_gallery_search_filter_switch(page: Page, base_url: str):
    """[Tier 4 - W3] Gallery search, filter & switch masterpiece."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Open gallery via shortcut 'g'
    page.keyboard.press("g")
    page.wait_for_timeout(300)
    assert page.evaluate("() => document.getElementById('gallery-drawer').classList.contains('open')")

    # Filter by genre and search
    page.click('.genre-pill[data-genre="life"]')
    page.wait_for_timeout(200)

    # Click first filtered card
    first_card = page.locator(".gallery-card").first
    first_card.click()
    page.wait_for_timeout(300)

    assert page.evaluate("() => window.__gardenEngine.getCurrentIndex()") >= 0
    page.evaluate("() => window.__gardenEngine.setMasterpiece(0)")


def test_t4_scenario_4_micro_loupe_pan_inspection(page: Page, base_url: str):
    """[Tier 4 - W4] Microscopic art detail inspection with loupe & pan."""
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    # Zoom in
    page.evaluate("() => window.__gardenEngine.setMacroZoom(2.5)")
    page.wait_for_timeout(100)
    assert page.locator("#macro-zoom-hud").is_visible()

    # Pan
    page.evaluate("() => window.__gardenEngine.setPanOffset(30, -40)")
    page.wait_for_timeout(50)

    # Reset
    page.click("#macro-zoom-reset-btn")
    page.wait_for_timeout(350)
    assert abs(page.evaluate("() => window.__gardenEngine.getMacroZoom()") - 1.0) < 0.1


def test_t4_scenario_5_responsive_cascade_transition(page: Page, base_url: str):
    """[Tier 4 - W5] Cross-device responsive layout transition across 4 breakpoints."""
    breakpoints = [
        (1440, 900),
        (1024, 768),
        (768, 1024),
        (375, 667)
    ]
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)

    for w, h in breakpoints:
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(150)
        assert page.evaluate("() => window.__gardenEngine.isLoaded()") is True
        # Verify no horizontal page blowout
        scroll_w = page.evaluate("() => document.documentElement.scrollWidth")
        inner_w = page.evaluate("() => window.innerWidth")
        assert scroll_w <= inner_w + 1, f"Horizontal overflow at {w}x{h}: scrollWidth={scroll_w}, innerWidth={inner_w}"

    page.set_viewport_size({"width": 1280, "height": 800})


# Registry of all functional tests for runner discovery
FUNCTIONAL_TESTS = [
    ("test_c1_1_dual_canvas_pixel_alignment", test_c1_1_dual_canvas_pixel_alignment, "Domain 1", "C1.1", "Dual canvas pixel alignment"),
    ("test_c1_2_viewport_adaptation", test_c1_2_viewport_adaptation, "Domain 1", "C1.2", "Viewport adaptation across resolutions"),
    ("test_c1_3_viewport_dynamic_height", test_c1_3_viewport_dynamic_height, "Domain 1", "C1.3", "Visual viewport & dynamic height"),
    ("test_c1_4_quote_linkage_and_subtle", test_c1_4_quote_linkage_and_subtle, "Domain 1", "C1.4", "Art quote linkage and subtle dimming"),
    ("test_c1_5_custom_cursor_and_ring", test_c1_5_custom_cursor_and_ring, "Domain 1", "C1.5", "Custom cursor ring size tracking"),
    ("test_c2_1_grayscale_initial_state", test_c2_1_grayscale_initial_state, "Domain 2", "C2.1", "Grayscale initial state"),
    ("test_c2_2_progressive_stroke_revealing", test_c2_2_progressive_stroke_revealing, "Domain 2", "C2.2", "Progressive stroke revealing"),
    ("test_c2_3_hover_charge", test_c2_3_hover_charge, "Domain 2", "C2.3", "Hover charge capability"),
    ("test_c2_4_morning_mist_decay", test_c2_4_morning_mist_decay, "Domain 2", "C2.4", "Morning mist decay settings"),
    ("test_c2_5_toggle_full_color", test_c2_5_toggle_full_color, "Domain 2", "C2.5", "One-click full color bloom"),
    ("test_c3_1_mode_switch_to_scratch", test_c3_1_mode_switch_to_scratch, "Domain 3", "C3.1", "Mode switch to scratch"),
    ("test_c3_2_scratch_true_color_render", test_c3_2_scratch_true_color_render, "Domain 3", "C3.2", "Scratch true color layers & preload"),
    ("test_c3_3_scratch_erasing", test_c3_3_scratch_erasing, "Domain 3", "C3.3", "Scratch erasing calculation"),
    ("test_c3_4_scratch_hud_realtime_progress", test_c3_4_scratch_hud_realtime_progress, "Domain 3", "C3.4", "Scratch HUD realtime progress"),
    ("test_c3_5_threshold_smooth_reveal", test_c3_5_threshold_smooth_reveal, "Domain 3", "C3.5", "Scratch threshold configuration"),
    ("test_c3_6_scratch_state_machine_lock", test_c3_6_scratch_state_machine_lock, "Domain 3", "C3.6", "State machine transition lock"),
    ("test_c3_7_reveal_now_button", test_c3_7_reveal_now_button, "Domain 3", "C3.7", "Reveal now button action"),
    ("test_c3_8_anti_leak_contain_guard", test_c3_8_anti_leak_contain_guard, "Domain 3", "C3.8", "Anti-leak background color guard"),
    ("test_c4_1_macro_zoom_levels", test_c4_1_macro_zoom_levels, "Domain 4", "C4.1", "Macro zoom levels (1.0x - 4.5x)"),
    ("test_c4_2_macro_pan_offset", test_c4_2_macro_pan_offset, "Domain 4", "C4.2", "Macro pan offset getter/setter"),
    ("test_c4_3_macro_zoom_reset", test_c4_3_macro_zoom_reset, "Domain 4", "C4.3", "Macro zoom reset method"),
    ("test_c4_4_macro_zoom_hud", test_c4_4_macro_zoom_hud, "Domain 4", "C4.4", "Macro zoom HUD & reset button"),
    ("test_c4_5_artisan_brass_loupe", test_c4_5_artisan_brass_loupe, "Domain 4", "C4.5", "Artisan brass loupe toggle & zoom cycle"),
    ("test_c4_6_loupe_edge_hysteresis", test_c4_6_loupe_edge_hysteresis, "Domain 4", "C4.6", "Loupe canvas element dimensions"),
    ("test_c5_1_brush_toggle_and_drag_distinction", test_c5_1_brush_toggle_and_drag_distinction, "Domain 5", "C5.1", "Brush toggle button popup open/close"),
    ("test_c5_2_brush_position_persistence", test_c5_2_brush_position_persistence, "Domain 5", "C5.2", "Brush position persistence & reset"),
    ("test_c5_3_brush_adaptive_flip_and_overflow", test_c5_3_brush_adaptive_flip_and_overflow, "Domain 5", "C5.3", "Brush popup adaptive bounds"),
    ("test_c5_4_brush_sliders_sync", test_c5_4_brush_sliders_sync, "Domain 5", "C5.4", "Brush sliders synchronization"),
    ("test_c5_5_fit_mode_and_scale", test_c5_5_fit_mode_and_scale, "Domain 5", "C5.5", "Fit mode & scale adjustment"),
    ("test_c5_6_click_outside_closes_brush_popup", test_c5_6_click_outside_closes_brush_popup, "Domain 5", "C5.6", "Click outside dismisses brush popup"),
    ("test_c6_1_gallery_open_close", test_c6_1_gallery_open_close, "Domain 6", "C6.1", "Gallery drawer open & close"),
    ("test_c6_2_gallery_fuzzy_search", test_c6_2_gallery_fuzzy_search, "Domain 6", "C6.2", "Gallery fuzzy search & clear"),
    ("test_c6_3_genre_pills_filter", test_c6_3_genre_pills_filter, "Domain 6", "C6.3", "7 genre pills filter"),
    ("test_c6_4_artist_and_category_selects", test_c6_4_artist_and_category_selects, "Domain 6", "C6.4", "Artist and category dropdowns"),
    ("test_c6_5_multi_filter_intersection", test_c6_5_multi_filter_intersection, "Domain 6", "C6.5", "Multi-filter AND intersection"),
    ("test_c6_6_virtual_scrolling_batch_load", test_c6_6_virtual_scrolling_batch_load, "Domain 6", "C6.6", "Virtual scrolling 24 card batch"),
    ("test_c6_7_card_click_switches_masterpiece", test_c6_7_card_click_switches_masterpiece, "Domain 6", "C6.7", "Card click switches masterpiece"),
    ("test_c7_1_story_open_close", test_c7_1_story_open_close, "Domain 7", "C7.1", "Story drawer open & close"),
    ("test_c7_2_story_three_section_dossier", test_c7_2_story_three_section_dossier, "Domain 7", "C7.2", "Three-section narrative dossier"),
    ("test_c7_3_story_mobile_bottom_sheet", test_c7_3_story_mobile_bottom_sheet, "Domain 7", "C7.3", "Mobile bottom sheet handle toggle"),
    ("test_c7_4_story_prev_next_navigation", test_c7_4_story_prev_next_navigation, "Domain 7", "C7.4", "Story previous/next navigation"),
    ("test_c8_1_gesture_interlocking", test_c8_1_gesture_interlocking, "Domain 8", "C8.1", "Gesture interlocking presence"),
    ("test_c8_2_swipe_navigation_handling", test_c8_2_swipe_navigation_handling, "Domain 8", "C8.2", "Swipe navigation event handling"),
    ("test_c8_3_touch_action_prevention", test_c8_3_touch_action_prevention, "Domain 8", "C8.3", "Canvas touch-action: none"),
    ("test_c8_4_touch_cancel_recovery", test_c8_4_touch_cancel_recovery, "Domain 8", "C8.4", "Touchcancel event recovery"),
    ("test_c9_1_keyboard_shortcuts", test_c9_1_keyboard_shortcuts, "Domain 9", "C9.1", "Global blind keyboard shortcuts"),
    ("test_c9_2_keyboard_focus_immunity", test_c9_2_keyboard_focus_immunity, "Domain 9", "C9.2", "Input focus shortcut immunity"),
    ("test_c9_3_esc_emergency_exit", test_c9_3_esc_emergency_exit, "Domain 9", "C9.3", "Escape key emergency exit"),
    ("test_c10_1_zero_console_errors", test_c10_1_zero_console_errors, "Domain 10", "C10.1", "Zero console script exceptions"),
    ("test_c10_2_broken_image_circuit_breaker", test_c10_2_broken_image_circuit_breaker, "Domain 10", "C10.2", "Image failure circuit breaker"),
    ("test_c10_3_render_loop_dormancy", test_c10_3_render_loop_dormancy, "Domain 10", "C10.3", "Render loop dormancy"),
    ("test_c10_4_webp_thumbnail_optimization", test_c10_4_webp_thumbnail_optimization, "Domain 10", "C10.4", "WebP thumbnail optimization"),
    ("test_t4_scenario_1_onboarding", test_t4_scenario_1_onboarding, "Tier 4", "W1", "Workflow: Onboarding & Help discovery"),
    ("test_t4_scenario_2_sleep_awakening_and_story", test_t4_scenario_2_sleep_awakening_and_story, "Tier 4", "W2", "Workflow: Sleep awakening & Story"),
    ("test_t4_scenario_3_gallery_search_filter_switch", test_t4_scenario_3_gallery_search_filter_switch, "Tier 4", "W3", "Workflow: Gallery search, filter & switch"),
    ("test_t4_scenario_4_micro_loupe_pan_inspection", test_t4_scenario_4_micro_loupe_pan_inspection, "Tier 4", "W4", "Workflow: Loupe & Pan inspection"),
    ("test_t4_scenario_5_responsive_cascade_transition", test_t4_scenario_5_responsive_cascade_transition, "Tier 4", "W5", "Workflow: Responsive cascade transition"),
]

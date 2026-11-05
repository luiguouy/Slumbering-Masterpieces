#!/usr/bin/env python3
"""
challenge_m3_stress.py - Empirical Adversarial Stress Suite for Milestone 3.
Authored by m3_challenger_2 (Runtime Stress, State Transitions, and Interaction Edge Cases).

Adversarial Stress Dimensions:
1. Rapid Interleaved Toggle Stress (>=25 rapid cycles):
   - Randomly/interleaved opening and closing of Gallery Drawer, Story Drawer, and Help Modal.
   - Tests opening another drawer while one is already open.
   - Tests closing via close buttons, got-it button, backdrop clicks, and ESC keys.
   - Verifies 0 stuck backdrop scrims, no body class desync ('gallery-open', 'story-open', 'help-open'),
     and 0 console errors.
2. Virtual Scrolling & Infinite Batch Stress:
   - Programmatically scrolls #gallery-list-container across continuous batches (24 -> 48 -> 72 -> 96 -> 120+ cards).
   - Oscillating rapid up/down scroll stress.
   - Verifies DOM stability, card index integrity, 4:3 thumbnail aspect ratio, grid column layouts,
     and memory/DOM element leak protection.
3. Filter & Search Stress:
   - Rapid sub-debounce typing bursts and search clear interactions.
   - Empty state verification (0 results) with full-grid spanning (grid-column: 1 / -1).
   - Rapid sequential genre pill switching.
   - Artist dropdown selection and multi-filter combination.
   - Interleaved chaotic filter/search stress followed by reset to 420 items.
4. ESC Key & Focus Hierarchy Stress:
   - Search input ESC clears query first, second ESC closes drawer.
   - Focus is cleanly blurred on close, preventing shortcut trapping.
   - Verification of global blind shortcuts (H, S, G, M) immediately after drawer/modal dismissal.
   - Multi-layer cross-component ESC hierarchy (Help Modal over Brush Popup).
"""

import math
import random
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
# Test 1: Rapid Interleaved Toggle Stress (>=25 rapid cycles)
# ------------------------------------------------------------------------------
def stress_rapid_interleaved_toggles(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(300)

    console_errors = []
    page_errors = []

    def on_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    def on_page_error(err):
        page_errors.append(str(err))

    page.on("console", on_console)
    page.on("pageerror", on_page_error)

    # 30 interleaved rapid cycles
    actions = [
        # Gallery triggers
        ("open_gallery_click", lambda: page.click("#open-gallery-modal-btn", force=True, timeout=1000)),
        ("open_gallery_key", lambda: page.keyboard.press("g")),
        ("close_gallery_btn", lambda: page.click("#gallery-close-btn", force=True, timeout=1000)),
        ("close_gallery_backdrop", lambda: page.click("#gallery-backdrop", force=True, timeout=1000)),
        ("close_gallery_esc", lambda: page.keyboard.press("Escape")),
        # Story triggers
        ("open_story_click", lambda: page.click("#story-toggle-btn", force=True, timeout=1000)),
        ("open_story_key", lambda: page.keyboard.press("s")),
        ("close_story_btn", lambda: page.click("#story-close-btn", force=True, timeout=1000)),
        ("close_story_backdrop", lambda: page.click("#story-backdrop", force=True, timeout=1000)),
        ("close_story_esc", lambda: page.keyboard.press("Escape")),
        # Help triggers
        ("open_help_click", lambda: page.click("#help-toggle-btn", force=True, timeout=1000)),
        ("open_help_key", lambda: page.keyboard.press("h")),
        ("close_help_btn", lambda: page.click("#help-close-btn", force=True, timeout=1000)),
        ("close_help_gotit", lambda: page.click("#help-got-it-btn", force=True, timeout=1000)),
        ("close_help_backdrop", lambda: page.click("#help-backdrop", force=True, timeout=1000)),
        ("close_help_esc", lambda: page.keyboard.press("Escape")),
    ]

    # Pre-defined interleaved sequence that includes opening on top of each other
    sequence = [
        # Cycle 1-5: Open Gallery, immediately open Story, then Help, then ESC cascade
        "open_gallery_click",
        "open_story_click",
        "open_help_click",
        "close_help_esc",
        "close_story_esc",
        # Cycle 6-10: Open Story, click backdrop, open Gallery, click close btn, open Help
        "open_story_key",
        "close_story_backdrop",
        "open_gallery_key",
        "close_gallery_btn",
        "open_help_key",
        # Cycle 11-15: Close help gotit, open Gallery, open Story on top, close story btn, close gallery esc
        "close_help_gotit",
        "open_gallery_click",
        "open_story_key",
        "close_story_btn",
        "close_gallery_esc",
        # Cycle 16-20: Rapid key toggles
        "open_help_click",
        "close_help_backdrop",
        "open_gallery_key",
        "close_gallery_backdrop",
        "open_story_click",
        # Cycle 21-25: Multi-switch
        "open_gallery_click",
        "open_help_key",
        "close_help_btn",
        "close_gallery_btn",
        "open_story_key",
        # Cycle 26-30: Rapid final burst
        "close_story_esc",
        "open_gallery_key",
        "open_story_click",
        "close_story_esc",
        "close_gallery_esc"
    ]

    action_map = dict(actions)
    step_results = []

    for idx, act_name in enumerate(sequence):
        try:
            action_map[act_name]()
            # Random micro delay between 20ms and 80ms simulating erratic user
            page.wait_for_timeout(random.randint(20, 80))
            step_results.append((idx + 1, act_name, "OK"))
        except Exception as e:
            step_results.append((idx + 1, act_name, f"ERR: {e}"))

    # Graceful recovery: press Escape twice and wait 300ms to ensure all settled
    page.keyboard.press("Escape")
    page.wait_for_timeout(100)
    page.keyboard.press("Escape")
    page.wait_for_timeout(350)

    # Now verify post-stress clean state:
    eval_state = page.evaluate("""() => {
        const body = document.body;
        const galleryDrawer = document.getElementById('gallery-drawer');
        const storyDrawer = document.getElementById('story-drawer');
        const helpModal = document.getElementById('help-modal');

        const galleryBackdrop = document.getElementById('gallery-backdrop') || document.querySelector('.gallery-backdrop');
        const storyBackdrop = document.getElementById('story-backdrop') || document.querySelector('.story-backdrop');
        const helpBackdrop = document.getElementById('help-backdrop') || document.querySelector('.help-backdrop');

        const getBackdropState = (el) => {
            if (!el) return { exists: false, blocking: false };
            const cs = window.getComputedStyle(el);
            const opacity = parseFloat(cs.opacity || '0');
            const pointerEvents = cs.pointerEvents;
            const display = cs.display;
            const visibility = cs.visibility;
            const isBlocking = (pointerEvents !== 'none' && opacity > 0.05 && display !== 'none' && visibility !== 'hidden');
            return {
                exists: true,
                opacity,
                pointerEvents,
                display,
                visibility,
                blocking: isBlocking
            };
        };

        return {
            bodyClasses: Array.from(body.classList),
            hasGalleryOpen: body.classList.contains('gallery-open'),
            hasStoryOpen: body.classList.contains('story-open'),
            hasHelpOpen: body.classList.contains('help-open'),
            galleryDrawerOpen: galleryDrawer ? galleryDrawer.classList.contains('open') : false,
            storyDrawerOpen: storyDrawer ? storyDrawer.classList.contains('open') : false,
            helpModalOpen: helpModal ? helpModal.classList.contains('open') : false,
            galleryBackdrop: getBackdropState(galleryBackdrop),
            storyBackdrop: getBackdropState(storyBackdrop),
            helpBackdrop: getBackdropState(helpBackdrop)
        };
    }""")

    # Verify clicking canvas is NOT blocked by any rogue backdrop
    canvas_clickable = False
    try:
        # Click center of canvas
        page.mouse.click(640, 400)
        page.wait_for_timeout(100)
        # Check active element or hit target
        hit_target = page.evaluate("""() => {
            const el = document.elementFromPoint(640, 400);
            return el ? el.id || el.className : 'null';
        }""")
        canvas_clickable = ("canvas" in str(hit_target).lower() or "stage" in str(hit_target).lower() or "quote" in str(hit_target).lower())
    except Exception:
        canvas_clickable = False

    no_body_desync = (not eval_state["hasGalleryOpen"] and not eval_state["hasStoryOpen"] and not eval_state["hasHelpOpen"])
    no_drawer_open = (not eval_state["galleryDrawerOpen"] and not eval_state["storyDrawerOpen"] and not eval_state["helpModalOpen"])
    no_stuck_scrim = (not eval_state["galleryBackdrop"]["blocking"] and not eval_state["storyBackdrop"]["blocking"] and not eval_state["helpBackdrop"]["blocking"])
    zero_console_errors = (len(console_errors) == 0 and len(page_errors) == 0)

    passed = (no_body_desync and no_drawer_open and no_stuck_scrim and canvas_clickable and zero_console_errors)

    return {
        "name": "Rapid Interleaved Toggle Stress (30 Cycles)",
        "passed": passed,
        "details": {
            "total_cycles": len(sequence),
            "no_body_desync": no_body_desync,
            "no_drawer_open": no_drawer_open,
            "no_stuck_scrim": no_stuck_scrim,
            "canvas_clickable": canvas_clickable,
            "console_errors_count": len(console_errors),
            "page_errors_count": len(page_errors),
            "eval_state": eval_state
        }
    }


# ------------------------------------------------------------------------------
# Test 2: Virtual Scrolling & Infinite Batch Stress (24 -> 48 -> 72 -> 96 -> 120+)
# ------------------------------------------------------------------------------
def stress_virtual_scrolling_continuous(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(200)

    # Open gallery
    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(350)

    # 1. Verify initial batch size is exactly 24
    initial_count = page.locator(".gallery-card").count()
    assert initial_count == 24, f"Initial batch should be 24, got {initial_count}"

    batch_checkpoints = []
    # Trigger scroll batches
    container = page.locator("#gallery-list-container")

    # Target batch sizes: 48, 72, 96, 120
    for target in [48, 72, 96, 120]:
        # Programmatically scroll container near the bottom
        page.evaluate("""() => {
            const c = document.getElementById('gallery-list-container');
            if (c) {
                c.scrollTop = c.scrollHeight;
                c.dispatchEvent(new Event('scroll'));
            }
        }""")
        # Wait up to 3s for batch to expand
        t0 = time.time()
        curr_count = page.locator(".gallery-card").count()
        while curr_count < target and (time.time() - t0) < 3.0:
            page.wait_for_timeout(100)
            curr_count = page.locator(".gallery-card").count()
            if curr_count < target:
                page.evaluate("""() => {
                    const c = document.getElementById('gallery-list-container');
                    if (c) c.scrollTop = c.scrollHeight;
                }""")

        batch_checkpoints.append({
            "target": target,
            "achieved": curr_count,
            "success": curr_count >= target,
            "elapsed_ms": round((time.time() - t0) * 1000, 1)
        })

    # Oscillating violent scrolling stress (scroll to top 0, then bottom, 5 times)
    for _ in range(5):
        page.evaluate("() => { const c = document.getElementById('gallery-list-container'); if (c) c.scrollTop = 0; }")
        page.wait_for_timeout(40)
        page.evaluate("() => { const c = document.getElementById('gallery-list-container'); if (c) c.scrollTop = c.scrollHeight; }")
        page.wait_for_timeout(40)

    final_card_count = page.locator(".gallery-card").count()

    # Deep DOM and CSS Grid audit on the loaded cards:
    dom_audit = page.evaluate("""() => {
        const container = document.getElementById('gallery-list-container');
        const cards = Array.from(document.querySelectorAll('.gallery-card'));
        const thumbBoxes = Array.from(document.querySelectorAll('.card-thumb-box'));
        const thumbImgs = Array.from(document.querySelectorAll('.card-thumb-img'));

        const containerCS = window.getComputedStyle(container);
        const gridCols = containerCS.gridTemplateColumns.split(' ').length;
        const display = containerCS.display;

        // Check cards
        const indices = cards.map(c => parseInt(c.getAttribute('data-index'), 10));
        const hasInvalidIndex = indices.some(idx => isNaN(idx) || idx < 0);
        const duplicates = indices.filter((item, index) => indices.indexOf(item) !== index);

        // Check thumb aspect ratio
        let invalidThumbCount = 0;
        thumbBoxes.slice(0, 48).forEach(box => {
            const rect = box.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                const ratio = rect.width / rect.height;
                // 4:3 is ~1.333
                if (Math.abs(ratio - 1.333) > 0.08) {
                    invalidThumbCount++;
                }
            }
        });

        // Check image srcs
        const missingSrcCount = thumbImgs.filter(img => !img.src || img.src.includes('undefined') || img.src.includes('null')).length;

        // Check DOM node count
        const totalElements = document.getElementsByTagName('*').length;

        return {
            display,
            gridCols,
            totalCards: cards.length,
            hasInvalidIndex,
            duplicateCount: duplicates.length,
            invalidThumbCount,
            missingSrcCount,
            totalDomElements: totalElements
        };
    }""")

    # Close gallery
    page.evaluate("() => window.__gardenEngine.closeGallery()")
    page.wait_for_timeout(200)

    all_batches_ok = all(b["success"] for b in batch_checkpoints)
    dom_ok = (dom_audit["display"] == "grid" and dom_audit["gridCols"] == 3 and
              not dom_audit["hasInvalidIndex"] and dom_audit["duplicateCount"] == 0 and
              dom_audit["invalidThumbCount"] == 0 and dom_audit["missingSrcCount"] == 0 and
              dom_audit["totalDomElements"] < 6000)

    passed = (all_batches_ok and dom_ok and final_card_count >= 120)

    return {
        "name": "Virtual Scrolling & Infinite Batch Stress (120+ cards)",
        "passed": passed,
        "details": {
            "initial_batch": initial_count,
            "final_card_count": final_card_count,
            "batch_checkpoints": batch_checkpoints,
            "dom_audit": dom_audit
        }
    }


# ------------------------------------------------------------------------------
# Test 3: Filter & Search Stress
# ------------------------------------------------------------------------------
def stress_filter_search_matrix(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(200)

    # Open gallery
    page.evaluate("() => window.__gardenEngine.openGallery()")
    page.wait_for_timeout(350)

    checks = []

    # 1. Rapid sub-debounce typing burst
    page.fill("#gallery-search-input", "日")
    page.wait_for_timeout(30)
    page.fill("#gallery-search-input", "莫奈")
    page.wait_for_timeout(30)
    page.fill("#gallery-search-input", "睡莲")
    # Wait debounce (180ms + buffer)
    page.wait_for_timeout(280)
    count_waterlilies = int(page.locator("#gallery-result-count").text_content().strip())
    checks.append({
        "check": "search_waterlilies",
        "pass": count_waterlilies > 0 and count_waterlilies < 420,
        "count": count_waterlilies
    })

    # 2. Instant clear button
    page.click("#gallery-search-clear")
    page.wait_for_timeout(100)
    count_after_clear = int(page.locator("#gallery-result-count").text_content().strip())
    checks.append({
        "check": "search_clear_button",
        "pass": count_after_clear == 420,
        "count": count_after_clear
    })

    # 3. Nonexistent query -> Empty state grid spanning test
    page.fill("#gallery-search-input", "NONEXISTENT_QUERY_XYZ_9999")
    page.wait_for_timeout(280)
    count_zero = int(page.locator("#gallery-result-count").text_content().strip())

    empty_state_audit = page.evaluate("""() => {
        const emptyEl = document.getElementById('gallery-empty-state') || document.querySelector('.gallery-empty-state');
        if (!emptyEl) return { exists: false };
        const cs = window.getComputedStyle(emptyEl);
        return {
            exists: true,
            display: cs.display,
            gridColumn: cs.gridColumn || cs.gridColumnStart + ' / ' + cs.gridColumnEnd,
            isVisible: cs.display !== 'none' && parseFloat(cs.opacity || '1') > 0
        };
    }""")
    checks.append({
        "check": "empty_state_layout",
        "pass": (count_zero == 0 and empty_state_audit["exists"] and
                 empty_state_audit["isVisible"] and "1 / -1" in empty_state_audit["gridColumn"]),
        "count": count_zero,
        "audit": empty_state_audit
    })

    # Clear again
    page.click("#gallery-search-clear")
    page.wait_for_timeout(100)

    # 4. Rapid clicking through all 7 genre pills
    genre_ids = page.evaluate("() => Array.from(document.querySelectorAll('.genre-pill')).map(p => p.getAttribute('data-genre'))")
    pills_ok = True
    genre_counts = {}
    for gid in genre_ids:
        page.click(f'.genre-pill[data-genre="{gid}"]')
        page.wait_for_timeout(60)
        c = int(page.locator("#gallery-result-count").text_content().strip())
        genre_counts[gid] = c
        # Active class test
        is_active = page.evaluate(f"""() => {{
            const pill = document.querySelector('.genre-pill[data-genre="{gid}"]');
            return pill ? pill.classList.contains('active') : false;
        }}""")
        if not is_active or c <= 0:
            pills_ok = False

    checks.append({
        "check": "rapid_genre_pills_cycling",
        "pass": pills_ok and genre_counts.get("all", 0) == 420,
        "counts": genre_counts
    })

    # 5. Artist dropdown test
    artist_val = page.evaluate("""() => {
        const sel = document.getElementById('artist-filter-select');
        return (sel && sel.options.length > 1) ? sel.options[1].value : null;
    }""")
    if artist_val:
        page.select_option("#artist-filter-select", value=artist_val)
        page.wait_for_timeout(100)
        artist_count = int(page.locator("#gallery-result-count").text_content().strip())
        checks.append({
            "check": "artist_filter_selection",
            "pass": artist_count > 0 and artist_count < 420,
            "artist": artist_val,
            "count": artist_count
        })

    # 6. Reset all filters
    # Ensure active filter exists so reset button is displayed
    page.click('.genre-pill[data-genre="landscape"]')
    page.wait_for_timeout(100)
    reset_visible = page.is_visible("#gallery-reset-btn")
    page.click("#gallery-reset-btn")
    page.wait_for_timeout(150)
    reset_state = page.evaluate("""() => {
        const input = document.getElementById('gallery-search-input');
        const artist = document.getElementById('artist-filter-select');
        const activeGenre = document.querySelector('.genre-pill.active');
        const count = parseInt(document.getElementById('gallery-result-count').textContent.trim(), 10);
        const cardCount = document.querySelectorAll('.gallery-card').length;
        const resetBtn = document.getElementById('gallery-reset-btn');

        return {
            inputValue: input ? input.value : 'missing',
            artistValue: artist ? artist.value : 'missing',
            genreId: activeGenre ? activeGenre.getAttribute('data-genre') : 'missing',
            count,
            cardCount,
            resetBtnHidden: resetBtn ? (resetBtn.style.display === 'none') : false
        };
    }""")
    reset_ok = (reset_visible and reset_state["inputValue"] == "" and reset_state["artistValue"] == "all" and
                reset_state["genreId"] == "all" and reset_state["count"] == 420 and
                reset_state["cardCount"] == 24 and reset_state["resetBtnHidden"])
    checks.append({
        "check": "gallery_reset_button",
        "pass": reset_ok,
        "state": reset_state
    })

    # 7. Chaotic interleaved filter stress (15 erratic interactions without waiting)
    for i in range(15):
        action_type = i % 3
        if action_type == 0:
            gid = genre_ids[i % len(genre_ids)]
            page.click(f'.genre-pill[data-genre="{gid}"]')
        elif action_type == 1:
            page.fill("#gallery-search-input", f"art_{i}")
        elif action_type == 2:
            if page.is_visible("#gallery-reset-btn"):
                page.click("#gallery-reset-btn")
        page.wait_for_timeout(20)

    # Final reset
    if page.is_visible("#gallery-reset-btn"):
        page.click("#gallery-reset-btn")
    else:
        page.click('.genre-pill[data-genre="landscape"]')
        page.wait_for_timeout(50)
        page.click("#gallery-reset-btn")
    page.wait_for_timeout(200)

    final_count = int(page.locator("#gallery-result-count").text_content().strip())
    final_cards = page.locator(".gallery-card").count()
    chaotic_ok = (final_count == 420 and final_cards == 24)
    checks.append({
        "check": "chaotic_interleaved_recovery",
        "pass": chaotic_ok,
        "final_count": final_count,
        "final_cards": final_cards
    })

    # Close gallery
    page.evaluate("() => window.__gardenEngine.closeGallery()")
    page.wait_for_timeout(200)

    all_passed = all(c["pass"] for c in checks)
    return {
        "name": "Filter & Search Stress Matrix",
        "passed": all_passed,
        "details": checks
    }


# ------------------------------------------------------------------------------
# Test 4: ESC Key & Focus Hierarchy Stress
# ------------------------------------------------------------------------------
def stress_esc_key_focus_shortcuts(page: Page, base_url: str) -> Dict[str, Any]:
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    page.wait_for_timeout(200)

    checks = []

    # 1. Open gallery, focus input, type text, 1st ESC clears text
    page.keyboard.press("g")
    page.wait_for_timeout(300)

    page.focus("#gallery-search-input")
    page.type("#gallery-search-input", "蒙娜丽莎")
    page.wait_for_timeout(100)

    # 1st ESC -> should clear query, drawer remains open
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)

    after_first_esc = page.evaluate("""() => {
        const input = document.getElementById('gallery-search-input');
        const drawer = document.getElementById('gallery-drawer');
        return {
            inputValue: input.value,
            drawerOpen: drawer.classList.contains('open')
        };
    }""")
    first_esc_ok = (after_first_esc["inputValue"] == "" and after_first_esc["drawerOpen"])
    checks.append({
        "check": "search_input_first_esc_clears",
        "pass": first_esc_ok,
        "details": after_first_esc
    })

    # 2nd ESC -> closes gallery drawer, removes body class, blur focus
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    after_second_esc = page.evaluate("""() => {
        const drawer = document.getElementById('gallery-drawer');
        const active = document.activeElement;
        const bodyHasClass = document.body.classList.contains('gallery-open');
        const isInputFocused = (active && active.id === 'gallery-search-input');
        return {
            drawerOpen: drawer.classList.contains('open'),
            bodyHasClass,
            isInputFocused,
            activeElementTag: active ? active.tagName : 'none'
        };
    }""")
    second_esc_ok = (not after_second_esc["drawerOpen"] and not after_second_esc["bodyHasClass"] and not after_second_esc["isInputFocused"])
    checks.append({
        "check": "search_input_second_esc_closes_and_blurs",
        "pass": second_esc_ok,
        "details": after_second_esc
    })

    # 2. Test global shortcuts (H, S, G, M) are NOT trapped
    # Test H -> opens help modal
    page.keyboard.press("h")
    page.wait_for_timeout(300)
    help_open = page.evaluate("() => document.getElementById('help-modal').classList.contains('open')")
    checks.append({"check": "shortcut_h_opens_help", "pass": help_open})

    # Focus got-it button inside help, press ESC -> closes help
    page.focus("#help-got-it-btn")
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    help_closed = page.evaluate("() => !document.getElementById('help-modal').classList.contains('open') && !document.body.classList.contains('help-open')")
    checks.append({"check": "esc_closes_help_and_body_class", "pass": help_closed})

    # Test S -> opens story drawer
    page.keyboard.press("s")
    page.wait_for_timeout(300)
    story_open = page.evaluate("() => document.getElementById('story-drawer').classList.contains('open') && document.body.classList.contains('story-open')")
    checks.append({"check": "shortcut_s_opens_story", "pass": story_open})

    # Focus close button in story, press ESC -> closes story
    page.focus("#story-close-btn")
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    story_closed = page.evaluate("() => !document.getElementById('story-drawer').classList.contains('open') && !document.body.classList.contains('story-open')")
    checks.append({"check": "esc_closes_story_and_body_class", "pass": story_closed})

    # Test G -> opens gallery drawer again
    page.keyboard.press("g")
    page.wait_for_timeout(300)
    gallery_open_again = page.evaluate("() => document.getElementById('gallery-drawer').classList.contains('open')")
    checks.append({"check": "shortcut_g_opens_gallery", "pass": gallery_open_again})

    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    # Test M -> toggles loupe
    page.keyboard.press("m")
    page.wait_for_timeout(200)
    loupe_on = page.evaluate("() => window.__gardenEngine.isLoupeEnabled()")
    page.keyboard.press("m")
    page.wait_for_timeout(200)
    loupe_off = page.evaluate("() => !window.__gardenEngine.isLoupeEnabled()")
    checks.append({"check": "shortcut_m_toggles_loupe", "pass": loupe_on and loupe_off})

    # 3. Multi-layer dismissal hierarchy: Brush popup + Help modal
    # Open brush popup
    page.click("#brush-toggle-btn")
    page.wait_for_timeout(200)
    brush_open = page.evaluate("() => document.getElementById('brush-popup').classList.contains('open')")

    # Open help modal on top
    page.click("#help-toggle-btn")
    page.wait_for_timeout(300)
    modal_open = page.evaluate("() => document.getElementById('help-modal').classList.contains('open')")

    # 1st ESC -> closes Help modal, Brush popup stays open
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    layer_esc_1 = page.evaluate("""() => {
        return {
            helpOpen: document.getElementById('help-modal').classList.contains('open'),
            brushOpen: document.getElementById('brush-popup').classList.contains('open')
        };
    }""")
    hierarchy_1_ok = (not layer_esc_1["helpOpen"] and layer_esc_1["brushOpen"])
    checks.append({
        "check": "multi_layer_first_esc_closes_top_modal",
        "pass": hierarchy_1_ok,
        "state": layer_esc_1
    })

    # 2nd ESC -> closes Brush popup
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    layer_esc_2 = page.evaluate("""() => {
        return {
            brushOpen: document.getElementById('brush-popup').classList.contains('open')
        };
    }""")
    hierarchy_2_ok = not layer_esc_2["brushOpen"]
    checks.append({
        "check": "multi_layer_second_esc_closes_brush_popup",
        "pass": hierarchy_2_ok,
        "state": layer_esc_2
    })

    all_passed = all(c["pass"] for c in checks)
    return {
        "name": "ESC Key & Focus Hierarchy Stress",
        "passed": all_passed,
        "details": checks
    }


def main():
    print("=" * 80)
    print(" ⚡ Milestone 3 Adversarial Stress Suite (m3_challenger_2)")
    print("=" * 80)

    with LocalServer() as server:
        base_url = server.base_url
        print(f" Local Server: {base_url}\n")

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            tests = [
                ("Stress 1: Rapid Interleaved Toggle Stress", stress_rapid_interleaved_toggles),
                ("Stress 2: Virtual Scrolling & Infinite Batch Stress", stress_virtual_scrolling_continuous),
                ("Stress 3: Filter & Search Stress Matrix", stress_filter_search_matrix),
                ("Stress 4: ESC Key & Focus Hierarchy Stress", stress_esc_key_focus_shortcuts),
            ]

            all_passed = True
            results = []

            for idx, (title, fn) in enumerate(tests, 1):
                start_t = time.time()
                print(f"[{idx}/{len(tests)}] Executing {title}...")
                try:
                    res = fn(page, base_url)
                    dur = (time.time() - start_t) * 1000
                    status = "PASSED" if res["passed"] else "FAILED"
                    if not res["passed"]:
                        all_passed = False
                    print(f"      Result: {status} ({dur:.1f}ms)")
                    results.append((title, status, dur, res))
                except Exception as exc:
                    dur = (time.time() - start_t) * 1000
                    all_passed = False
                    print(f"      Result: EXCEPTION ({dur:.1f}ms) — {exc}")
                    results.append((title, "EXCEPTION", dur, {"error": str(exc)}))

            browser.close()

            print("\n" + "=" * 80)
            print(" 📊 ADVERSARIAL STRESS SUMMARY")
            print("=" * 80)
            for title, status, dur, res in results:
                symbol = "✓" if status == "PASSED" else "✗"
                print(f" {symbol} {title:<55} [{status}] ({dur:6.1f}ms)")

            print("=" * 80)
            print(f" OVERALL: {'ALL PASSED (4/4)' if all_passed else 'FAILURES DETECTED'}")
            print("=" * 80)

            return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

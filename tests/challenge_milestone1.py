#!/usr/bin/env python3
"""
challenge_milestone1.py - Empirical Adversarial Stress Harness for Milestone 1.

Written by: m1_challenger_1 (EMPIRICAL CHALLENGER)
Purpose:
- Rigorously test and challenge claims of Milestone 1.
- Challenge 1: Mathematical precision of grid column widths across 15 viewports.
- Challenge 2: Heading line-height and margin closures (k * 24px) for all h1-h6 variants and sibling combinations.
- Challenge 3: Asymmetric margin tension ratios (2:3:4:6) across desktop, tablet, and mobile.
- Challenge 4: Stage immersion, canvas coordinate matching, and zero-leak overflow under DOM injection.
- Challenge 5: Token commensurability and Z-index monotonic hierarchy.
"""

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


# ==============================================================================
# Challenge 1: Grid Column Formula Across 15 Arbitrary Viewports
# ==============================================================================
def challenge_grid_math_viewports(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test CSS Grid column calculation:
    Cw = [W_body - (N - 1) * G] / N
    and gutter absorption for spans 1..N.
    """
    test_viewports = [
        2560, 1920, 1680, 1440, 1366, 1280, 1024, # Desktop / Widescreen
        1023, 900, 834, 768,                        # Tablet (8 cols)
        767, 600, 480,                             # Mobile Large (4 cols)
        479, 375, 320                              # Mobile Small (2 cols)
    ]
    
    failures = []
    viewport_results = []
    
    for vp_w in test_viewports:
        page.set_viewport_size({"width": vp_w, "height": 900})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        
        # Inject test grid container into the DOM
        res = page.evaluate("""() => {
            let container = document.getElementById('test-swiss-grid');
            if (container) container.remove();
            
            container = document.createElement('div');
            container.id = 'test-swiss-grid';
            container.className = 'swiss-grid';
            
            // Add 12 columns
            for (let i = 1; i <= 12; i++) {
                const col = document.createElement('div');
                col.className = 'col-span-1 test-col';
                col.id = `col-${i}`;
                col.textContent = `C${i}`;
                container.appendChild(col);
            }
            
            // Add spanned columns
            const spanClasses = ['col-span-2', 'col-span-3', 'col-span-4', 'col-span-6', 'col-span-8', 'col-span-12'];
            spanClasses.forEach(cls => {
                const spanCol = document.createElement('div');
                spanCol.className = `${cls} test-span-col`;
                spanCol.id = `span-${cls}`;
                container.appendChild(spanCol);
            });
            
            document.body.appendChild(container);
            
            const cs = window.getComputedStyle(container);
            const gridRect = container.getBoundingClientRect();
            const padL = parseFloat(cs.paddingLeft) || 0;
            const padR = parseFloat(cs.paddingRight) || 0;
            const colGap = parseFloat(cs.columnGap) || 0;
            const bodyWidth = gridRect.width - padL - padR;
            
            // Read CSS variable for columns
            const gridColsVar = parseInt(cs.getPropertyValue('--grid-columns').trim(), 10) || 12;
            
            // Measure actual widths of individual 1-col items
            const col1 = document.getElementById('col-1');
            const col1Rect = col1.getBoundingClientRect();
            
            // Measure span widths
            const spans = {};
            spanClasses.forEach(cls => {
                const el = document.getElementById(`span-${cls}`);
                spans[cls] = el ? el.getBoundingClientRect().width : 0;
            });
            
            container.remove();
            
            return {
                gridWidth: gridRect.width,
                bodyWidth,
                padL,
                padR,
                colGap,
                gridColsVar,
                measuredCol1Width: col1Rect.width,
                spans
            };
        }""")
        
        N = res['gridColsVar']
        G = res['colGap']
        W_body = res['bodyWidth']
        expected_Cw = (W_body - (N - 1) * G) / N
        measured_Cw = res['measuredCol1Width']
        
        # Check column width match (tolerance 0.75px for subpixel rendering)
        diff = abs(measured_Cw - expected_Cw)
        passed = diff <= 0.75
        
        # Check gutter absorption on spans according to responsive folding rules
        # In desktop (>=1024): 1..12 spans are 1..12.
        # In tablet (768..1023, 8 cols):
        #   col-span-12..8 -> span 8
        #   col-span-7..6  -> span 8
        #   col-span-5..3  -> span 4
        #   col-span-2     -> span 2
        # In mobile (480..767, 4 cols):
        #   col-span-12..4 -> span 4
        #   col-span-3     -> span 4
        #   col-span-2     -> span 2
        # In small mobile (<480, 2 cols):
        #   col-span-12..2 -> span 2
        #   col-span-1     -> span 1
        def get_folded_span(span_count, cols):
            if cols == 12:
                return span_count
            elif cols == 8:
                if span_count >= 6:
                    return 8
                elif span_count >= 3:
                    return 4
                else:
                    return 2
            elif cols == 4:
                if span_count >= 3:
                    return 4
                else:
                    return 2
            elif cols == 2:
                if span_count >= 2:
                    return 2
                else:
                    return 1
            return min(span_count, cols)

        span_failures = []
        for cls, measured_span_w in res['spans'].items():
            span_count = int(cls.replace('col-span-', ''))
            folded_span = get_folded_span(span_count, N)
            expected_span_w = folded_span * measured_Cw + (folded_span - 1) * G
            span_diff = abs(measured_span_w - expected_span_w)
            if span_diff > 1.0:  # subpixel accumulated difference allowance
                span_failures.append(f"{cls} (folds to {folded_span}): expected={expected_span_w:.2f}px, got={measured_span_w:.2f}px (diff={span_diff:.2f})")
        
        vp_stat = {
            "viewport": vp_w,
            "columns": N,
            "gutter": G,
            "bodyWidth": round(W_body, 2),
            "expected_Cw": round(expected_Cw, 2),
            "measured_Cw": round(measured_Cw, 2),
            "diff": round(diff, 3),
            "passed": passed and len(span_failures) == 0,
            "span_failures": span_failures
        }
        viewport_results.append(vp_stat)
        
        if not passed or len(span_failures) > 0:
            failures.append(vp_stat)

    return {
        "test": "Grid Mathematics Across 15 Viewports",
        "passed": len(failures) == 0,
        "total_viewports": len(test_viewports),
        "failures_count": len(failures),
        "failures": failures,
        "results": viewport_results
    }


# ==============================================================================
# Challenge 2: Heading Mathematical Closures & Baseline Alignments
# ==============================================================================
def challenge_heading_closures(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test line-height closures for all heading tags (h1-h6),
    compact variants, and adjacent sibling pairs:
    Margin_top + Line_height + Margin_bottom = k * 24px (k in Z+).
    """
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    
    data = page.evaluate("""() => {
        const tests = [
            { tag: 'h1', class: '' },
            { tag: 'h1', class: 'compact' },
            { tag: 'h2', class: '' },
            { tag: 'h2', class: 'compact' },
            { tag: 'h3', class: '' },
            { tag: 'h3', class: 'compact' },
            { tag: 'h4', class: '' },
            { tag: 'h4', class: 'compact' },
            { tag: 'h5', class: '' },
            { tag: 'h6', class: '' },
            { tag: 'p', class: '' },
            { tag: 'p', class: 'compact' }
        ];
        
        const container = document.createElement('div');
        container.style.visibility = 'hidden';
        document.body.appendChild(container);
        
        const results = [];
        tests.forEach(t => {
            const el = document.createElement(t.tag);
            if (t.class) el.className = t.class;
            el.textContent = `Sample ${t.tag} ${t.class}`;
            container.appendChild(el);
            // Append a sibling dummy so :last-child is not triggered
            const dummy = document.createElement('span');
            container.appendChild(dummy);
            
            const cs = window.getComputedStyle(el);
            const mt = parseFloat(cs.marginTop) || 0;
            const mb = parseFloat(cs.marginBottom) || 0;
            const lh = parseFloat(cs.lineHeight) || 0;
            const total = mt + lh + mb;
            
            results.push({
                element: t.class ? `${t.tag}.${t.class}` : t.tag,
                marginTop: mt,
                lineHeight: lh,
                marginBottom: mb,
                total: total,
                k: total / 24,
                isMultipleOf24: Math.abs((total % 24)) < 0.05 || Math.abs((total % 24) - 24) < 0.05
            });
            el.remove();
            dummy.remove();
        });
        
        // Test adjacent sibling closures:
        // h1 + h2, h2 + h3, h3 + h4, h1 + p, h2 + p
        const pairs = [
            ['h1', 'h2'],
            ['h2', 'h3'],
            ['h3', 'h4'],
            ['h1', 'p'],
            ['h2', 'p']
        ];
        
        const pairResults = [];
        pairs.forEach(([tag1, tag2]) => {
            const el1 = document.createElement(tag1);
            el1.textContent = `Sibling ${tag1}`;
            const el2 = document.createElement(tag2);
            el2.textContent = `Sibling ${tag2}`;
            container.appendChild(el1);
            container.appendChild(el2);
            
            const cs1 = window.getComputedStyle(el1);
            const cs2 = window.getComputedStyle(el2);
            
            const r1 = el1.getBoundingClientRect();
            const r2 = el2.getBoundingClientRect();
            
            // Distance from top of el1 to bottom of el2
            const spanHeight = r2.bottom - r1.top;
            
            pairResults.push({
                pair: `${tag1} + ${tag2}`,
                el1_lh: parseFloat(cs1.lineHeight),
                el1_mb: parseFloat(cs1.marginBottom),
                el2_mt: parseFloat(cs2.marginTop),
                el2_lh: parseFloat(cs2.lineHeight),
                spanHeight: spanHeight,
                k_24: spanHeight / 24,
                k_12: spanHeight / 12,
                isMultipleOf24: Math.abs((spanHeight % 24)) < 0.1 || Math.abs((spanHeight % 24) - 24) < 0.1,
                isMultipleOf12: Math.abs((spanHeight % 12)) < 0.1 || Math.abs((spanHeight % 12) - 12) < 0.1
            });
            el1.remove();
            el2.remove();
        });
        
        container.remove();
        return { headings: results, pairs: pairResults };
    }""")
    
    # Heading closure strictly applies to h1-h6 as per DISPATCH instructions
    heading_failures = [h for h in data['headings'] if h['element'].startswith('h') and not h['isMultipleOf24']]
    para_failures = [h for h in data['headings'] if h['element'] == 'p' and not h['isMultipleOf24']]
    failures = heading_failures + para_failures
    
    return {
        "test": "Heading Mathematical Closures & Baseline Alignments",
        "passed": len(failures) == 0,
        "failures_count": len(failures),
        "failures": failures,
        "headings": data['headings'],
        "pairs": data['pairs']
    }


# ==============================================================================
# Challenge 3: Asymmetric Margin Tension (2:3:4:6)
# ==============================================================================
def challenge_margin_proportions(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test Müller-Brockmann 2:3:4:6 progression across Desktop, Tablet, Mobile.
    """
    viewports = [
        {"name": "Desktop (>=1024px)", "width": 1280, "expected": (16, 24, 32, 48)},
        {"name": "Tablet (768-1023px)", "width": 800, "expected": (12, 18, 24, 36)},
        {"name": "Mobile (<=767px)", "width": 375, "expected": (8, 12, 16, 24)}
    ]
    
    results = []
    failures = []
    
    for vp in viewports:
        page.set_viewport_size({"width": vp["width"], "height": 800})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        
        pads = page.evaluate("""() => {
            const el = document.createElement('div');
            el.className = 'module-box-asymmetric';
            document.body.appendChild(el);
            const cs = window.getComputedStyle(el);
            const pL = parseFloat(cs.paddingLeft) || 0;
            const pT = parseFloat(cs.paddingTop) || 0;
            const pR = parseFloat(cs.paddingRight) || 0;
            const pB = parseFloat(cs.paddingBottom) || 0;
            el.remove();
            return { pL, pT, pR, pB };
        }""")
        
        expL, expT, expR, expB = vp["expected"]
        pass_inner = abs(pads["pL"] - expL) < 0.1
        pass_top = abs(pads["pT"] - expT) < 0.1
        pass_outer = abs(pads["pR"] - expR) < 0.1
        pass_bottom = abs(pads["pB"] - expB) < 0.1
        
        # Check strict inequality: Inner < Top < Outer < Bottom
        strictly_increasing = pads["pL"] < pads["pT"] < pads["pR"] < pads["pB"]
        
        # Check 2:3:4:6 ratio
        unit = pads["pL"] / 2
        ratio_valid = (
            abs(pads["pT"] - 3 * unit) < 0.1 and
            abs(pads["pR"] - 4 * unit) < 0.1 and
            abs(pads["pB"] - 6 * unit) < 0.1
        )
        
        all_ok = pass_inner and pass_top and pass_outer and pass_bottom and strictly_increasing and ratio_valid
        
        res_item = {
            "viewport": vp["name"],
            "padding": pads,
            "expected": {"pL": expL, "pT": expT, "pR": expR, "pB": expB},
            "ratio_valid": ratio_valid,
            "strictly_increasing": strictly_increasing,
            "passed": all_ok
        }
        results.append(res_item)
        if not all_ok:
            failures.append(res_item)
            
    return {
        "test": "Asymmetric Margin Tension (2:3:4:6)",
        "passed": len(failures) == 0,
        "failures_count": len(failures),
        "failures": failures,
        "details": results
    }


# ==============================================================================
# Challenge 4: Stage Immersion, Overflow Leakage & Dynamic Stress
# ==============================================================================
def challenge_stage_overflow_and_canvases(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test full viewport immersion (100dvh) and zero scroll leaks
    under aggressive dynamic element injections.
    """
    viewports = [1920, 1440, 1024, 768, 375]
    failures = []
    
    for w in viewports:
        page.set_viewport_size({"width": w, "height": 800})
        page.goto(f"{base_url}/index.html")
        wait_engine_ready(page)
        
        res = page.evaluate("""() => {
            const stage = document.getElementById('art-stage');
            const bg = document.getElementById('bg-canvas');
            const rev = document.getElementById('reveal-canvas');
            
            const stageRect = stage.getBoundingClientRect();
            const bgRect = bg.getBoundingClientRect();
            const revRect = rev.getBoundingClientRect();
            
            // Initial scroll check
            const docScrollW = document.scrollingElement.scrollWidth;
            const docScrollH = document.scrollingElement.scrollHeight;
            const winW = window.innerWidth;
            const winH = window.innerHeight;
            
            const initialNoScroll = (docScrollW <= winW) && (docScrollH <= winH);
            
            // Now inject an aggressive 3000px tall element inside art-stage
            const testSpill = document.createElement('div');
            testSpill.style.width = '3000px';
            testSpill.style.height = '3000px';
            testSpill.style.position = 'absolute';
            testSpill.style.top = '500px';
            testSpill.style.left = '500px';
            stage.appendChild(testSpill);
            
            // Check if document scrolling is still strictly zero
            const stressScrollW = document.scrollingElement.scrollWidth;
            const stressScrollH = document.scrollingElement.scrollHeight;
            const leakPrevented = (stressScrollW <= winW) && (stressScrollH <= winH);
            
            testSpill.remove();
            
            // Dual canvas alignment check
            const canvasAligns = (
                Math.abs(bgRect.width - stageRect.width) < 0.1 &&
                Math.abs(bgRect.height - stageRect.height) < 0.1 &&
                Math.abs(revRect.width - stageRect.width) < 0.1 &&
                Math.abs(revRect.height - stageRect.height) < 0.1
            );
            
            return {
                viewport: { w: winW, h: winH },
                initialNoScroll,
                leakPrevented,
                canvasAligns,
                stageRect: { w: stageRect.width, h: stageRect.height }
            };
        }""")
        
        ok = res["initialNoScroll"] and res["leakPrevented"] and res["canvasAligns"]
        if not ok:
            failures.append({"viewport": w, "result": res})
            
    return {
        "test": "Stage Immersion, Overflow Leakage & Dynamic Stress",
        "passed": len(failures) == 0,
        "failures_count": len(failures),
        "failures": failures
    }


# ==============================================================================
# Challenge 5: Token Monotonicity & Commensurability
# ==============================================================================
def challenge_tokens_and_z_index(page: Page, base_url: str) -> Dict[str, Any]:
    """
    Stress-test spatial tokens (8pt system commensurability)
    and Z-index monotonic strict ordering.
    """
    page.goto(f"{base_url}/index.html")
    wait_engine_ready(page)
    
    token_eval = page.evaluate("""() => {
        const root = document.documentElement;
        const cs = window.getComputedStyle(root);
        
        // Spatial tokens check
        const spatial = [
            '--space-1', '--space-2', '--space-3', '--space-4',
            '--space-5', '--space-6', '--space-8', '--space-10',
            '--space-12', '--space-16'
        ];
        
        const spaceVals = spatial.map(s => {
            const val = parseFloat(cs.getPropertyValue(s).trim());
            return { token: s, val, is4pt: (val % 4) === 0 };
        });
        
        // Z-Index hierarchy
        const zTokens = [
            '--z-stage',
            '--z-canvas',
            '--z-quote',
            '--z-hud',
            '--z-controls',
            '--z-drawer-backdrop',
            '--z-drawer',
            '--z-modal-backdrop',
            '--z-modal',
            '--z-toast',
            '--z-loupe',
            '--z-cursor',
            '--z-topmost'
        ];
        
        const zVals = zTokens.map(z => {
            return { token: z, val: parseInt(cs.getPropertyValue(z).trim(), 10) };
        });
        
        let zStrictlyMonotonic = true;
        for (let i = 0; i < zVals.length - 1; i++) {
            if (zVals[i].val >= zVals[i + 1].val) {
                zStrictlyMonotonic = false;
                break;
            }
        }
        
        return {
            spaceVals,
            zVals,
            zStrictlyMonotonic,
            allSpatial4pt: spaceVals.every(s => s.is4pt)
        };
    }""")
    
    passed = token_eval["allSpatial4pt"] and token_eval["zStrictlyMonotonic"]
    return {
        "test": "Token Commensurability & Z-Index Hierarchy",
        "passed": passed,
        "token_eval": token_eval
    }


def main():
    print("=" * 80)
    print(" ⚔️  EMPIRICAL CHALLENGER (m1_challenger_1) — Milestone 1 Stress Harness")
    print("=" * 80)
    
    with LocalServer() as server:
        base_url = server.base_url
        print(f" Local Server running at {base_url}")
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Run Challenge 1
            print("\n[1/5] Running Challenge 1: Grid Mathematics Across 15 Viewports...")
            c1 = challenge_grid_math_viewports(page, base_url)
            print(f"      Passed: {c1['passed']} (Tested {c1['total_viewports']} viewports, Failures: {c1['failures_count']})")
            if not c1['passed']:
                for f in c1['failures']:
                    print(f"      [FAIL] Viewport {f['viewport']}px: {f}")
            
            # Run Challenge 2
            print("\n[2/5] Running Challenge 2: Heading Mathematical Closures & Baseline...")
            c2 = challenge_heading_closures(page, base_url)
            print(f"      Passed: {c2['passed']} (Tested {len(c2['headings'])} headings, Failures: {c2['failures_count']})")
            for h in c2['headings']:
                print(f"      - {h['element']}: mt={h['marginTop']}px, lh={h['lineHeight']}px, mb={h['marginBottom']}px -> Total={h['total']}px (k={h['k']}) [OK: {h['isMultipleOf24']}]")
            print("      Adjacent Sibling Pairs:")
            for pair in c2['pairs']:
                print(f"      - {pair['pair']}: span={pair['spanHeight']}px (k24={pair['k_24']:.2f}, k12={pair['k_12']:.2f}) [Multiple of 12px: {pair['isMultipleOf12']}, Multiple of 24px: {pair['isMultipleOf24']}]")
                
            # Run Challenge 3
            print("\n[3/5] Running Challenge 3: Asymmetric Margin Tension (2:3:4:6)...")
            c3 = challenge_margin_proportions(page, base_url)
            print(f"      Passed: {c3['passed']} (Failures: {c3['failures_count']})")
            for d in c3['details']:
                p = d['padding']
                print(f"      - {d['viewport']}: Left={p['pL']}px, Top={p['pT']}px, Right={p['pR']}px, Bottom={p['pB']}px (Ratio 2:3:4:6: {d['ratio_valid']})")
                
            # Run Challenge 4
            print("\n[4/5] Running Challenge 4: Stage Immersion, Overflow & Canvas Alignments...")
            c4 = challenge_stage_overflow_and_canvases(page, base_url)
            print(f"      Passed: {c4['passed']} (Failures: {c4['failures_count']})")
            
            # Run Challenge 5
            print("\n[5/5] Running Challenge 5: Token Commensurability & Z-Index...")
            c5 = challenge_tokens_and_z_index(page, base_url)
            print(f"      Passed: {c5['passed']} (4pt Spacing: {c5['token_eval']['allSpatial4pt']}, Monotonic Z-Index: {c5['token_eval']['zStrictlyMonotonic']})")
            
            browser.close()
            
            all_passed = c1['passed'] and c2['passed'] and c3['passed'] and c4['passed'] and c5['passed']
            print("\n" + "=" * 80)
            if all_passed:
                print(" 🏆 FINAL CHALLENGE RESULT: ALL ADVERSARIAL STRESS TESTS PASSED (100%)")
            else:
                print(" ❌ FINAL CHALLENGE RESULT: ADVERSARIAL FAILURES DETECTED")
            print("=" * 80)
            
            return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

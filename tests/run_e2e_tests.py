#!/usr/bin/env python3
"""
run_e2e_tests.py - Unified CLI Runner for art-web E2E Test Suite.

Executes:
1. Functional Non-Regression Suite (46 Checklist items across 10 domains + Tier 4 Workflows)
2. Müller-Brockmann 15-Item Grid Design System Audit Suite

Outputs:
- Live terminal execution logs with timings and status indicators
- Structured JSON report at tests/reports/e2e_results.json
- Exits with code 0 on all tests passing, non-zero on any failure.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

# Ensure tests package can be resolved
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.server_helper import LocalServer
from tests.test_functional_non_regression import FUNCTIONAL_TESTS
from tests.test_grid_design_audit import GRID_AUDIT_TESTS

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright is not installed. Run 'pip install playwright' and 'playwright install chrome'.")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="art-web E2E Test Runner")
    parser.add_argument(
        "--suite",
        choices=["all", "functional", "audit"],
        default="all",
        help="Test suite to run (default: all)"
    )
    parser.add_argument(
        "--channel",
        default="chrome",
        help="Browser channel for Playwright (default: chrome, fallback to chromium)"
    )
    parser.add_argument(
        "--report",
        default="tests/reports/e2e_results.json",
        help="Output path for JSON report (default: tests/reports/e2e_results.json)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose test details"
    )
    return parser.parse_args()


def run_tests():
    args = parse_args()
    report_path = PROJECT_ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" 🏛️  Masterpiece Garden (art-web) — Comprehensive E2E Test Suite")
    print("=" * 80)
    print(f" Timestamp:  {datetime.now(timezone.utc).isoformat()}")
    print(f" Test Suite: {args.suite}")
    print(f" Browser:    Chromium (channel: {args.channel})")
    print(f" Report:     {report_path}")
    print("-" * 80)

    start_total_time = time.time()
    results: List[Dict[str, Any]] = []
    audit_scorecard: List[Dict[str, Any]] = []
    failed_count = 0
    passed_count = 0

    with LocalServer() as server:
        base_url = server.base_url
        print(f" Local HTTP Daemon: {base_url} (serving {PROJECT_ROOT})\n")

        with sync_playwright() as p:
            # Launch browser with requested channel (with graceful fallback to default chromium)
            browser = None
            try:
                browser = p.chromium.launch(channel=args.channel, headless=True)
            except Exception as e:
                print(f" [!] Channel '{args.channel}' launch failed ({e}), falling back to standard chromium.")
                browser = p.chromium.launch(headless=True)

            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            # ------------------------------------------------------------------
            # 1. Functional Non-Regression Test Execution
            # ------------------------------------------------------------------
            if args.suite in ["all", "functional"]:
                print(f"▶ Running Functional Non-Regression Suite ({len(FUNCTIONAL_TESTS)} tests)...")
                print("-" * 80)

                for test_name, test_fn, domain, checklist_id, desc in FUNCTIONAL_TESTS:
                    test_start = time.time()
                    status = "PASSED"
                    error_msg = None

                    try:
                        test_fn(page, base_url)
                        passed_count += 1
                        dur = (time.time() - test_start) * 1000
                        print(f"  ✓ [{checklist_id}] {desc:<50} ({dur:6.1f}ms)")
                    except Exception as exc:
                        status = "FAILED"
                        failed_count += 1
                        dur = (time.time() - test_start) * 1000
                        error_msg = str(exc)
                        print(f"  ✗ [{checklist_id}] {desc:<50} ({dur:6.1f}ms) — FAIL: {error_msg}")

                    results.append({
                        "id": checklist_id,
                        "name": test_name,
                        "domain": domain,
                        "description": desc,
                        "status": status,
                        "duration_ms": round(dur, 2),
                        "error": error_msg
                    })

                print()

            # ------------------------------------------------------------------
            # 2. Müller-Brockmann 15-Item Grid Design System Audit Execution
            # ------------------------------------------------------------------
            if args.suite in ["all", "audit"]:
                print(f"▶ Running Müller-Brockmann 15-Item Grid Design System Audit...")
                print("-" * 80)

                for audit_name, audit_fn, audit_id, desc in GRID_AUDIT_TESTS:
                    audit_start = time.time()
                    status = "PASSED"
                    error_msg = None
                    audit_res = None

                    try:
                        audit_res = audit_fn(page, base_url)
                        passed_count += 1
                        dur = (time.time() - audit_start) * 1000
                        detail = audit_res.get("detail", "")
                        print(f"  ✓ [{audit_id}] {desc:<48} ({dur:6.1f}ms)")
                        if args.verbose and detail:
                            print(f"      └─ {detail}")
                    except Exception as exc:
                        status = "FAILED"
                        failed_count += 1
                        dur = (time.time() - audit_start) * 1000
                        error_msg = str(exc)
                        print(f"  ✗ [{audit_id}] {desc:<48} ({dur:6.1f}ms) — FAIL: {error_msg}")

                    audit_entry = {
                        "id": audit_id,
                        "name": audit_name,
                        "domain": "Grid Design System Audit",
                        "description": desc,
                        "status": status,
                        "score": 100 if status == "PASSED" else 0,
                        "duration_ms": round(dur, 2),
                        "detail": audit_res.get("detail", "") if audit_res else error_msg,
                        "error": error_msg
                    }
                    results.append(audit_entry)
                    audit_scorecard.append(audit_entry)

                print()

            browser.close()

    total_duration = time.time() - start_total_time
    total_tests = passed_count + failed_count
    pass_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0.0

    # Summary by Domain
    domain_summary: Dict[str, Dict[str, int]] = {}
    for r in results:
        dom = r["domain"]
        if dom not in domain_summary:
            domain_summary[dom] = {"total": 0, "passed": 0, "failed": 0}
        domain_summary[dom]["total"] += 1
        if r["status"] == "PASSED":
            domain_summary[dom]["passed"] += 1
        else:
            domain_summary[dom]["failed"] += 1

    report_data = {
        "metadata": {
            "title": "art-web E2E Test Suite Report",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_duration_seconds": round(total_duration, 2),
            "browser": "Chromium (channel: chrome)",
            "suite_filter": args.suite
        },
        "summary": {
            "total_tests": total_tests,
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate_percent": round(pass_rate, 2),
            "status": "PASSED" if failed_count == 0 else "FAILED"
        },
        "domain_summary": domain_summary,
        "audit_scorecard": audit_scorecard,
        "test_results": results
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print(" 📊 E2E TEST SUMMARY")
    print("=" * 80)
    print(f" Total Tests Executed: {total_tests}")
    print(f" Passed:               {passed_count}")
    print(f" Failed:               {failed_count}")
    print(f" Pass Rate:            {pass_rate:.1f}%")
    print(f" Total Time:           {total_duration:.2f}s")
    print(f" JSON Report Saved:    {report_path}")
    print("=" * 80)

    if failed_count == 0:
        print("\n 🎉 ALL TESTS PASSED! Project is ready for milestone certification.\n")
        sys.exit(0)
    else:
        print(f"\n ❌ {failed_count} TEST(S) FAILED. Please review errors above.\n")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()

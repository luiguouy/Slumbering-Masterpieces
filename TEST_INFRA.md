# E2E Test Infra: art-web

## Test Philosophy
- Opaque-box, requirement-driven, independent of implementation internals.
- Dual testing objectives:
  1. Functional Non-Regression: 100% preservation of all 10 domains and 46 interactive features in `art-web`.
  2. Grid Design System Audit: Rigorous validation of the 15-item Swiss grid design system standards based on Müller-Brockmann principles.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Interaction + Real-World Art Gallery Workflows.

## Feature Inventory
| # | Feature | Source (Requirement) | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Workload) |
|---|---------|----------------------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| 1 | App Boot & Masterpieces Data | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 2 | Dual Mode Switching | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 3 | Canvas Engine & Scratching | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 4 | Micro-Loupe Exploration | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 5 | Brush Panel Controls | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 6 | Gallery Drawer & Search | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 7 | Story Drawer & Narratives | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 8 | Help Modal & Shortcuts | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 9 | Margin Proportions & Optical Center | SKILL.md Items 2 & 4 | 5 | 5 | ✓ | ✓ |
| 10 | Baseline Continuity & Heading Closure | SKILL.md Items 9 & 10 | 5 | 5 | ✓ | ✓ |
| 11 | Grid Column Spanning & Gutter Absorption | SKILL.md Items 5 & 12 | 5 | 5 | ✓ | ✓ |
| 12 | Responsive Breakpoints Cascade | SKILL.md Item 8 | 5 | 5 | ✓ | ✓ |
| 13 | Typography Scale & Line Length | SKILL.md Items 6 & 7 | 5 | 5 | ✓ | ✓ |
| 14 | Negative Space & Visual Weight Balance | SKILL.md Items 13, 14 & 15 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **Runtime Environment**: Python 3.10+ with `playwright` (Chromium/Chrome channel).
- **Server Lifecycle**: Local multithreaded HTTP server dynamically bound on localhost.
- **Entry Points**:
  - Full Runner: `python tests/run_e2e_tests.py`
  - Automated Reports: `tests/reports/e2e_results.json` and human-readable console output.
- **Pass/Fail Semantics**: Exit code 0 on all tests passing, non-zero on any failure.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | First-time Visitor Onboarding & Help Discovery | F1, F8, F9, F13 | Medium |
| 2 | Sleep Mode Awakening & Story Reading Flow | F1, F2, F3, F7, F10 | High |
| 3 | Gallery Search, Filter & Switch Masterpiece | F1, F6, F7, F11 | High |
| 4 | Microscopic Art Detail Inspection with Loupe & Pan | F1, F3, F4, F5 | High |
| 5 | Cross-Device Responsive Layout Transition | F9, F10, F11, F12, F13 | High |

## Coverage Thresholds
- Tier 1: ≥5 per feature (70+ test cases)
- Tier 2: ≥5 per feature across boundary conditions (70+ test cases)
- Tier 3: Pairwise combinations across major features (20+ test cases)
- Tier 4: Realistic end-to-end user workflows (5 application scenarios)
- Total planned test cases: 165+

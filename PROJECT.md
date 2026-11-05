# Project: art-web Grid Design System Optimization & Refactoring

## Architecture
- **Design Philosophy**: Swiss International Typographic Style (Josef Müller-Brockmann).
- **Core Layout Architecture**:
  - CSS Grid 12-column modular framework with proportional margins ($Inner:Top:Outer:Bottom = 2:3:4:6$) and 8pt token system.
  - Baseline Grid ($L_{\text{base}} = 24\text{px}$) with typographic harmonic scale and strict line-height closure ($k \cdot L_{\text{base}}$).
  - Responsive folding cascade: $12 \to 8 \to 4 \to 2$ across widescreen, desktop, tablet, and mobile.
  - Optical center alignment ($44\% \sim 46\%$) for central floating elements.
- **Frontend Architecture**:
  - Native ES Modules (Zero-build) with 11 domain modules in `js/` coordinated by `js/main.js`.
  - DOM contract preservation: 100% retention of all 87 DOM IDs and 26 interactive classes.
  - Dynamic Art Stage Canvas decoupled from HTML/CSS structural overlay.
- **Verification Strategy**:
  - Dual Track: Implementation Track + E2E Testing Track.
  - Automated Playwright E2E suite covering 46-point non-regression checklist and 15-item Grid Design System audit.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Design Token System | Centralized `:root` CSS variables for 8pt spacing, typographic scales, semantic colors, border-radiuses, and z-index hierarchy | M1 | Survey (arch & spec) |
| 2 | Baseline Grid & Typography Engine | 24px vertical baseline grid, typographic harmonic scale, line-height closure formula ($\text{Margin}_t + H_L + \text{Margin}_b = k \cdot L_{\text{base}}$) | M1 | Survey (spec) |
| 3 | Swiss Grid Framework Classes | Reusable 12-column grid container (`.swiss-grid`), column spanning (`.col-span-*`), gutter absorption, and module field utilities | M1 | Survey (spec & arch) |
| 4 | Art Quote Geometric Alignment | Optical center ($44\% \sim 46\%$) placement, comfortable reading line length (30-45 CJK characters), baseline locked leading | M2 | Survey (arch) |
| 5 | Floating Controls & HUDs Baseline Lock | Perfect bottom-edge baseline alignment for Mode Switcher & Help Button (eliminating 2px offset to 0.00px), Scratch HUD & Loupe HUD tokenization | M2 | Survey (arch) |
| 6 | Brush Control Modular Integration | Brush button and popup tokenized styling, 8pt metrics, preserving drag coordinates and PointerCapture persistence | M2 | Survey (func & arch) |
| 7 | Gallery Drawer Multi-Column Grid | Modular multi-column card grid adapting from 1 to 3 columns, preserving 400px WebP thumbnails and virtual loading | M3 | Survey (arch & func) |
| 8 | Story Drawer Typographic Layout | 3-section structured archive layout, font scale rhythm, baseline alignment, and responsive drawer widths | M3 | Survey (arch & func) |
| 9 | Help Modal Modular Matrix | 8-column modal dialog layout with 2-column internal grid for mechanics and keyboard shortcuts | M3 | Survey (arch & func) |
| 10 | Responsive Breakpoint Cascade | Smooth folding across 4 breakpoints: Widescreen (>=1440px, 12-col), Desktop (1024-1439px, 12-col), Tablet (768-1023px, 8-col), Mobile (<=767px, 4/2-col) | M4 | Survey (arch) |
| 11 | Typography & CJK Font Stack | High-legibility font stack combining Cormorant/Garamond with PingFang SC/Hiragino/Microsoft YaHei/SongTi fallback, text contrast enhancement | M4 | Survey (arch) |
| 12 | Structural Negative Space & Polish | Elimination of 133 ad-hoc RGBA strings and 20 random radiuses, lever principle asymmetric balance, clean negative space | M4 | Survey (spec & arch) |
| 13 | E2E Test Suite Infrastructure & Harness | Playwright-based test harness, local HTTP server orchestration, CLI runner with pass/fail semantics | E2E-Track | Survey (func) |
| 14 | Functional Non-Regression Test Cases | Automated test coverage for all 10 domains and 46 checklist items (modes, canvas, loupe, gallery, story, shortcuts) | E2E-Track | Survey (func) |
| 15 | 15-Item Grid Design System Audit Tests | Automated verification suite checking all 15 Müller-Brockmann audit criteria via DOM measurements and computed styles | E2E-Track | Survey (spec) |
| 16 | Final Integration & Adversarial Hardening | 100% pass across all Tier 1-4 tests, plus Tier 5 adversarial edge-case stress testing and coverage hardening | M5 | Survey (all) |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Suite | Requirements-driven test infrastructure, 46-point non-regression tests, and 15-item grid audit suite | none | DONE |
| M1 | Grid Tokens & Core Layout Foundation | CSS `:root` tokens, baseline grid rules, typographic scale, Swiss Grid utility classes, base container layout | none | DONE |
| M2 | Floating Controls & Art Stage Alignment | Art quote optical center, mode switcher, help button, brush panel, HUDs baseline alignment and tokenization | M1 | DONE |
| M3 | Drawers & Modals Modular Refactoring | Gallery drawer multi-col grid, Story drawer typography & baseline lock, Help modal matrix | M1, M2 | DONE |
| M4 | Responsive Breakpoint Cascade & Polish | Breakpoint cascade (12->8->4->2), CJK font stack, contrast & negative space cleanup, final style integration | M2, M3 | DONE |
| M5 | 100% E2E Pass & Adversarial Hardening | Pass 100% of E2E test suite (Tiers 1-4), adversarial Tier 5 tests, forensic audit, completion report | E2E, M4 | DONE |

## Interface Contracts
### M1 Foundation ↔ M2/M3 Components
- **CSS Custom Properties**:
  - Spacing Tokens: `--space-1` (4px), `--space-2` (8px), `--space-3` (12px), `--space-4` (16px), `--space-5` (20px), `--space-6` (24px), `--space-8` (32px), `--space-10` (40px), `--space-12` (48px), `--space-16` (64px).
  - Baseline Token: `--baseline: 24px` (sub-rhythm: `--baseline-half: 12px`, `--baseline-quarter: 6px`).
  - Grid Tokens: `--grid-columns: 12`, `--grid-gutter: 24px`, `--grid-margin: clamp(24px, 5vw, 64px)`, `--max-width: 1440px`.
  - Type Scale: `--font-xs: 0.75rem` (12px), `--font-sm: 0.875rem` (14px), `--font-base: 1rem` (16px), `--font-md: 1.125rem` (18px), `--font-lg: 1.25rem` (20px), `--font-xl: 1.5rem` (24px), `--font-2xl: 2rem` (32px), `--font-3xl: 2.5rem` (40px), `--font-4xl: 3rem` (48px).
  - Line Heights: Locked to multiples of baseline or baseline halves: `--lh-tight: 1.25`, `--lh-base: 1.5` (24px on 16px text), `--lh-relaxed: 1.75`.
  - Z-Index Matrix: `--z-stage: 1`, `--z-canvas: 2`, `--z-quote: 10`, `--z-hud: 20`, `--z-controls: 30`, `--z-drawer-backdrop: 40`, `--z-drawer: 50`, `--z-modal-backdrop: 60`, `--z-modal: 70`, `--z-toast: 80`, `--z-loupe: 90`.
- **DOM Stability Contract**:
  - All existing 87 IDs (`#art-stage`, `#bg-canvas`, `#reveal-canvas`, `#brush-control`, `#gallery-drawer`, `#story-drawer`, `#help-modal`, etc.) MUST remain intact.
  - All interactive state classes (`.open`, `.active`, `.is-active`, `.macro-panning`, etc.) MUST remain untouched.
  - Grid classes (`.swiss-grid`, `.col-span-*`) are additive only.

### E2E Test Runner ↔ Implementation Track
- **Execution Protocol**:
  - Test runner command: `python tests/run_e2e_tests.py`
  - Exit code 0 on all tests passing, non-zero on failure.
  - JSON test report generated at `tests/reports/e2e_results.json`.

## Code Layout
- `index.html`: Entry point, semantic layout structure, modal/drawer markup.
- `style.css`: Primary stylesheet, structured into:
  - Part 1: Design Tokens & CSS Variables (`:root`) [DONE in M1]
  - Part 2: Reset & Swiss Typographic Rhythm [DONE in M1]
  - Part 3: Swiss Grid System & Modular Utilities [DONE in M1]
  - Part 4: Stage & Visual Canvas Overlay [DONE in M1]
  - Part 5: Floating HUDs & Navigation Controls [DONE in M2]
  - Part 6: Drawers (Gallery & Story) [Scope for M3]
  - Part 7: Dialogs (Help Modal & Toast) [Scope for M3]
  - Part 8: Responsive Breakpoints Media Queries [Scope for M4]
- `js/`: ESM modules (strictly preserve behavior and public APIs).
- `tests/`: E2E test suites and runner scripts [DONE in E2E Track].
- `docs/`: Design documentation and SVG wireframes.

# The Underdog Casino — Roulette Simulator & Analytics Suite

> *A full-stack roulette simulation engine with terminal UI, statistical analysis, pattern detection, and a live browser dashboard — built entirely in Python and vanilla JavaScript.*

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
  - [Terminal Simulator (`roulette_casino.py`)](#terminal-simulator)
  - [Live Dashboard (`casino_dashboard.html`)](#live-dashboard)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Running the Simulator](#running-the-simulator)
  - [Opening the Dashboard](#opening-the-dashboard)
- [Usage Guide](#usage-guide)
  - [Main Menu](#main-menu)
  - [Session Reports Menu](#session-reports-menu)
  - [Batch Spin Buttons (Dashboard)](#batch-spin-buttons-dashboard)
- [Architecture](#architecture)
  - [Core Classes](#core-classes)
  - [Module Overview](#module-overview)
- [Statistical Methods](#statistical-methods)
- [Screenshots](#screenshots)
- [License](#license)

---

## Overview

The Underdog Casino is a two-part roulette analytics project:

1. **`roulette_casino.py`** — A richly styled terminal application that simulates European roulette (numbers 0–36, uniform distribution), tracks every outcome, detects statistical patterns, and generates HTML reports.

2. **`casino_dashboard.html`** — A standalone browser dashboard with a fully animated canvas roulette wheel, six live-updating Chart.js panels, single-spin mode, auto-spin mode, and batch simulation (10 K / 50 K / 100 K spins) — all with no server or build step required.

Both files are **zero-dependency** beyond Python's standard library and a CDN-delivered Chart.js script.

---

## Project Structure

```
underdog-casino/
│
├── roulette_casino.py        # Terminal simulator + analytics engine
├── casino_dashboard.html     # Live browser dashboard (standalone)
└── README.md                 # This file
```

**Generated at runtime** (not committed):

```
casino_spins_YYYYMMDD_HHMMSS.csv    # Raw spin export
casino_spins_YYYYMMDD_HHMMSS.json   # Raw spin export (JSON)
casino_viz_YYYYMMDD_HHMMSS.html     # Static snapshot dashboard
casino_live_YYYYMMDD_HHMMSS.html    # Live dashboard copy
```

---

## Features

### Terminal Simulator

#### Simulation Engine
- European roulette — numbers **0 through 36**, 37 equally probable outcomes
- Uniform distribution via Python's `random.randint(0, 36)`
- Speed: **2–3 million spins per second** on modern hardware
- Run sizes: 1 (animated), 1 K, 10 K, 100 K, 1 M

#### Outcome Tracker (`OutcomeTracker`)
Logs every spin and computes in real time:

| Feature | Detail |
|---|---|
| Win/Loss streaks | Colour streaks (red/black/zero) and parity streaks (odd/even), with running max |
| Number frequency | Hit count, percentage, deviation from expected for all 37 pockets |
| Distribution over time | Session split into 10 equal segments — red %, black %, zero %, odd %, even % per segment |
| Category breakdowns | Colour split, odd/even, 1st/2nd/3rd dozen, low/high halves |
| Chi-square stat | Full 37-number goodness-of-fit test (χ², df=36) |
| Sparklines | ASCII block sparklines for red/black drift over time |

#### Pattern Detection Engine (`PatternDetector`)
Three independent statistical modules run after any simulation:

**Module 1 — Streak Irregularity**
- Fits observed streak-length histogram against the geometric series expectation: `P(k) = p·(1−p)^(k−1)`
- Computes a Kolmogorov–Smirnov statistic comparing cumulative observed vs. expected distributions
- Outputs an **Irregularity Score (0–100)** scaled against the KS critical value at 5%
- Flags individual length anomalies (>50% over- or under-represented)

**Module 2 — Outcome Clustering**
- Adaptive sliding window (~2% of session length) scans the full spin sequence
- For each window position computes **Z = (observed − μ) / σ** under `Binomial(W, p)`
- Windows with |Z| > 3.09 (p < 0.001) are flagged as hot or cold clusters
- Covers: colour clusters, individual number hotspots, dozen clusters

**Module 3 — Deviation from Expected**
- Per-number **Z-scores** with two-tailed p-values (normal approximation)
- Flag thresholds: |Z| > 2.576 (99%) and |Z| > 3.291 (99.9%)
- Four **chi-square tests**: all 37 numbers, colour split, odd/even, dozens
- Overall verdict: `[OK]` / `[~]` / `[!]` / `[!!!]`

#### Reports Available (Terminal)
| Key | Report |
|-----|--------|
| `1` | Classic frequency table with bar charts |
| `2` | Croupier summary (red/black/zero counts, hottest/coldest numbers, χ²) |
| `3` | Streak report — colour & parity streaks with histogram |
| `4` | Frequency deep-dive — per-number with deviation, 4 category breakdowns |
| `5` | Distribution over time — 10-segment table + sparklines |
| `6` | All three tracker reports |
| `7` | Pattern Detection Engine |
| `8` | Full analysis — all tracker + pattern reports |
| `v` | Generate HTML dashboard (opens in browser) |
| `9` | Export raw data → CSV + JSON |

#### Export Formats
- **CSV**: `spin_index, number, colour, parity, dozen, half, timestamp`
- **JSON**: full metadata + per-spin records + frequency counts + streak summary

---

### Live Dashboard

**`casino_dashboard.html`** — open directly in any modern browser, no server needed.

#### The Roulette Wheel
- Rendered on an HTML5 `<canvas>` element using the authentic **European pocket order**: `0, 32, 15, 19, 4, 21, 2, 25, 17, 34, ...`
- Gold ornamental rim (conic-gradient), bevelled hub with 8 spokes, animated ivory ball
- Gold pointer triangle fixed at 12 o'clock
- Smooth **ease-out deceleration** animation (8–12 full rotations, ~3.5 seconds)
- Click the wheel or the spin button to trigger

#### Spin Modes
| Control | Behaviour |
|---|---|
| **◆ Spin the Wheel ◆** | Single spin with full wheel animation |
| **Auto Spin** | Continuous spins at selected speed (Slow / Normal / Fast / Turbo) |
| **10,000 Spins** | Batch: one wheel animation, 10 K data points processed |
| **50,000 Spins** | Batch: one wheel animation, 50 K data points processed |
| **100,000 Spins** | Batch: one wheel animation, 100 K data points processed |
| **Reset** | Clears all state and resets all charts to zero |

**Batch spin architecture**: All random numbers are generated upfront in O(n). The wheel animates once to the final landing number. Data is then processed in 5,000-spin chunks via `requestAnimationFrame`, keeping the browser responsive. A live progress bar shows `Processing… N / Total` with percentage.

#### Six Live Charts (Chart.js 4.4)

| # | Chart | Updates |
|---|---|---|
| I | **Expected vs Actual** — bar chart for all 37 numbers with gold expected line | Every spin |
| II | **Frequency Density Curve** — Gaussian KDE (σ=1.5) envelope | Every 10 spins |
| III | **Colour · Parity · Dozen Split** — 8-category grouped bars with expected markers | Every spin |
| IV | **Running Red %** — convergence line toward 48.65% | Every spin |
| V | **Streak Distribution vs Geometric Model** — purple bars + gold geometric curve | Every spin |
| VI | **Deviation Z-Scores** — per-number bars coloured by significance | Every spin |

Z-score colour key: 🟢 Normal | 🟡 Z > 1.5 | 🔴 Z > 2.58 (flagged) | 🔵 Z < −1.5

#### History Strip
Last 30 results shown as colour-coded chips. Batch runs append a gold summary tag instead of individual chips.

---

## Getting Started

### Requirements

**Terminal simulator:**
- Python 3.10 or higher
- No third-party packages — only standard library modules: `random`, `math`, `csv`, `json`, `collections`, `datetime`
- A terminal with ANSI 24-bit colour support (macOS Terminal, iTerm2, Windows Terminal, most Linux terminals)

**Live dashboard:**
- Any modern browser (Chrome, Firefox, Safari, Edge)
- Internet connection on first open (loads Chart.js and Google Fonts from CDN)
- Or download Chart.js locally and update the `<script>` src

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/underdog-casino.git
cd underdog-casino
```

No virtual environment or `pip install` needed.

### Running the Simulator

```bash
python roulette_casino.py
```

You will see the main menu:

```
========================================================================
                    +  GRAND CASINO ROYALE  +
         Established 1875  .  Monte Carlo, Monaco
------------------------------------------------------------------------
     - La Roulette Europeenne  .  Pattern Detection Suite -
========================================================================

  Choose your table:

  [1]  Single animated spin
  [2]  Quick run                            (1,000 spins)
  [3]  Standard run                         (10,000 spins)
  [4]  Grand run                            (100,000 spins)
  [5]  High Roller -- one million           (1,000,000 spins)

  [q]  Quit
```

### Opening the Dashboard

Simply double-click `casino_dashboard.html` or open it in your browser:

```bash
# macOS
open casino_dashboard.html

# Linux
xdg-open casino_dashboard.html

# Windows
start casino_dashboard.html
```

The dashboard can also be generated from within the terminal simulator by running a simulation and selecting `[v]` from the session reports menu.

---

## Usage Guide

### Main Menu

| Key | Action |
|-----|--------|
| `1` | Single animated spin — watch the wheel scroll through numbers |
| `2` | Quick run — 1,000 spins (completes in < 1 ms) |
| `3` | Standard run — 10,000 spins |
| `4` | Grand run — 100,000 spins |
| `5` | High Roller — 1,000,000 spins (~350 ms) |
| `q` | Quit |

### Session Reports Menu

After any multi-spin run completes, the session reports menu appears. All reports are computed from the current session's data and can be viewed in any combination.

### Batch Spin Buttons (Dashboard)

Batch buttons are styled in crimson to distinguish them from single-spin controls. During a batch:

1. All N random numbers are generated instantly in JavaScript
2. The wheel spins once to the final landing pocket
3. Data is processed in 5,000-spin chunks with a progress bar
4. All six charts refresh simultaneously when processing completes

Batches **accumulate** on top of existing data — run multiple batches to build up a large dataset progressively.

---

## Architecture

### Core Classes

#### `OutcomeTracker`
Stateful log of all spins in the current session.

```python
tracker = OutcomeTracker()
tracker.record(17)                    # single spin
tracker.record_batch([4, 22, 0, 7])   # bulk insert
tracker.flush_streaks()               # close open streak at session end

tracker.frequency()          # Counter: {num: hits}
tracker.colour_frequency()   # {'red': N, 'black': N, 'zero': N}
tracker.streak_summary()     # nested dict of streak stats
tracker.distribution_over_time(segments=10)  # list of segment dicts
tracker.export_csv('out.csv')
tracker.export_json('out.json')
```

#### `PatternDetector`
Stateless analyser — takes a tracker, returns structured dicts.

```python
pd = PatternDetector(tracker)

pd.streak_irregularity()    # KS test vs geometric model
pd.clustering_analysis()    # sliding-window Z-test
pd.deviation_analysis()     # per-number Z-scores + chi-square
```

### Module Overview

```
roulette_casino.py
│
├── Constants & helpers
│   ├── ANSI colour palette (24-bit RGB)
│   ├── RED_NUMBERS / BLACK_NUMBERS sets
│   └── num_color(), colour_of(), parity_of(), dozen_of(), half_of()
│
├── Visual helpers
│   ├── hr(), center(), print_header()
│   └── spinning_animation()  — ASCII wheel scroll
│
├── OutcomeTracker              (lines ~105–212)
│   ├── record() / record_batch()
│   ├── _update_streaks() / flush_streaks()
│   ├── frequency / colour_frequency / parity_frequency / ...
│   ├── distribution_over_time()
│   └── export_csv() / export_json()
│
├── PatternDetector             (lines ~215–550)
│   ├── streak_irregularity()   — KS stat vs geometric series
│   ├── clustering_analysis()   — sliding Z-window
│   └── deviation_analysis()    — z-scores + chi-square battery
│
├── Display functions           (lines ~555–970)
│   ├── print_pattern_detection()
│   ├── print_streak_report()
│   ├── print_frequency_report()
│   ├── print_distribution_report()
│   ├── build_frequency_table()
│   └── build_summary()
│
├── Visualization               (lines ~971–1780)
│   ├── generate_visualization_html()  — static snapshot
│   └── _write_live_dashboard()        — copies casino_dashboard.html
│
└── Menus                       (lines ~1780–1917)
    ├── tracker_menu()
    └── menu() / main()
```

---

## Statistical Methods

| Method | Description |
|---|---|
| **Uniform random** | `random.randint(0, 36)` — Mersenne Twister PRNG, 37 equiprobable outcomes |
| **Chi-square (χ²)** | Goodness-of-fit, df=36. Verdict: `χ² < 54` = Excellent, `< 72` = Good |
| **Z-score** | `(observed − μ) / σ` where `μ = n/37`, `σ = √(n·p·(1−p))`. Flags at 2.58σ (99%) and 3.29σ (99.9%) |
| **KS statistic** | Kolmogorov–Smirnov max cumulative deviation of streak lengths vs geometric model |
| **Geometric model** | Streak length k expected with probability `p_break · p_cont^(k−1)` |
| **Binomial Z-test** | Sliding window clustering: `Z = (count − W·p) / √(W·p·(1−p))` |
| **Gaussian KDE** | Frequency density: kernel `K(x) = exp(−0.5·((x−xᵢ)/σ)²) / (σ√2π)`, σ=1.5 |
| **Wilson–Hilferty** | Normal approximation for chi-square p-values |

---

## Screenshots

### Terminal — Main Menu
```
+ GRAND CASINO ROYALE +
Established 1875 . Monte Carlo, Monaco
- La Roulette Europeenne . Pattern Detection Suite -
```

### Terminal — Pattern Detection (Module 2 excerpt)
```
MODULE 2  |  OUTCOME CLUSTERING DETECTION
Sliding-window Z-test: flags local concentrations (|Z|>3.09, p<0.001)

Window size: 200 spins (~2.0% of session)

-- Colour Clusters
Colour     Hot Windows  Cold Windows  Assessment
red               0             2     CLUSTERS DETECTED
  COLD at spin  8288: count=75 in 200 spins  Z=-3.15
```

### Dashboard — Live Charts
Six panels update in real time after every spin:
- Chart I: Bar chart, 37 numbers, gold expected line
- Chart IV: Running red % converging toward 48.65%
- Chart VI: Z-score bars, green→amber→red by significance

---

## License

MIT License — free to use, modify, and distribute.

```
Copyright (c) 2025 The Underdog Casino

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

---

*The house always wins — but now you can see exactly how.*

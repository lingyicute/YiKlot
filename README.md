<br>
<br>
<br>
<br>
<p align="center">
  <img src="./assets/icon.png" alt="YiKlot Logo" width="96" height="96" onerror="this.style.display='none'"/>
</p>
<h1 align="center">YiKlot</h1>
<h3 align="center">Slide and shift, mind gets swift!</h3>

<p align="center">A clean, lightweight, and privacy-first 数字华容道 (Number Klotski) game, crafted with Material You and modern web engineering.</p>
<p align="center">Made with ❤️ by <a href="https://github.com/lingyicute">lingyicute</a>.</p>
<br>
<br>
<p align="center">
  [🇺🇸 English] •
  <a href="https://github.com/lingyicute/YiKlot">🌐 Source Code</a> •
  <a href="https://github.com/lingyicute/YiKlot/issues">🐛 Report Bug</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-orange.svg" alt="License: AGPL-3.0"></a>
  <a href="index.html"><img src="https://img.shields.io/badge/Single%20File-137%20KB-blue" alt="Single File 137 KB"></a>
  <a href="https://github.com/lingyicute/YiKlot"><img src="https://img.shields.io/badge/Dependencies-Zero-brightgreen" alt="Zero Dependencies"></a>
  <a href="https://github.com/lingyicute/YiKlot"><img src="https://img.shields.io/badge/Ads%20%26%20Trackers-Zero-brightgreen" alt="No Ads No Tracking"></a>
  <a href="https://github.com/lingyicute/YiKlot"><img src="https://img.shields.io/github/stars/lingyicute/YiKlot?style=flat&color=yellow" alt="GitHub Stars"></a>
</p>
<br>

## 📖 Overview

数字华容道 (Number Klotski / $N^2-1$ Puzzle) has one mathematical trap that trips up naive implementations: **exactly half of all random permutations are unsolvable**. Even worse, many browser clones only allow clicking one adjacent tile at a time and offer no assistance once a player gets stuck on a 5×5 or 6×6 board.

**YiKlot** guarantees every generated board is strictly solvable via exact inversion-parity verification, supports smooth **multi-tile row/column pushing** alongside touch swipes and keyboard controls, and embeds a millisecond-fast solver for instant **next-move hints** across all board sizes from **3×3 up to 6×6** — shipped as **one self-contained HTML file**.

<br>

## ✨ Features

- **🧠 Provably Solvable & Fluid Mechanics**
  - Exact inversion + blank-row parity check guarantees **100% solvable boards** across both odd (3×3, 5×5) and even (4×4, 6×6) dimensions, with non-trivial initial Manhattan distance.
  - **Multi-tile line push**: tapping or dragging any tile in the same row or column as the blank smoothly glides the entire segment together with hardware-accelerated FLIP animations.

- **🛟 Smart Assists**
  - **Hint (提示)** runs an exact stage-reduction BFS + 3×3 linear-conflict IDA* solver in milliseconds to highlight the optimal next tile (and executes the move automatically if tapped again).
  - **Mark (标位)** highlights tiles already standing on their home coordinates and softly reveals the target number inside the empty slot.
  - **Undo (撤销)** & **Restart (重新开始)** step backward cleanly or deal a fresh board in one tap, with automatic mid-game state persistence.

- **🎯 Four Board Sizes**
  - **简单 Easy** 3×3 (8 tiles) · **中等 Medium** 4×4 (15 tiles) · **困难 Hard** 5×5 (24 tiles) · **专家 Expert** 6×6 (35 tiles).
  - Hint budgets scale with difficulty (5 / 8 / 12 / 16 hints).

- **🎨 Material You & Full Viewport Adaptivity**
  - **Dynamic theming**: eight accents built on `oklch` tonal ramps, Light / Dark modes following OS preference, live `theme-color` sync, and `prefers-reduced-motion` support.
  - **Adaptive across every viewport width**: seamlessly scales via CSS container queries (`cqw`) and multi-tier responsive layouts across narrow phones, tablets, landscape mobile, and wide desktop screens.

- **🔒 100% Privacy, Offline & Ad-Free**
  - **Zero network requests** — markup, styles, solver, and subsetted `Nebulove` + `Yomi-UI-Emoji` fonts are embedded into `index.html`.
  - Records (`yk-best`), preferences (`yk-theme`, `yk-palette`, `yk-diff`), and progress (`yk-state`) stay strictly local.
  - Licensed under **AGPL-3.0**.

<br>

## 🚀 Play It Now

There is nothing to install — the game *is* one HTML file.

### Option 1 — Just open it
Download `index.html` (or clone the repository) and double-click the file. It works straight from disk, offline.

### Option 2 — Serve it locally
```bash
git clone https://github.com/lingyicute/YiKlot.git
cd YiKlot
python3 -m http.server 8000     # then open http://localhost:8000
```

### Option 3 — Publish it anywhere
Drop `index.html` on GitHub Pages, Cloudflare Pages, Netlify or any static host — a single file is the entire deployment.

<br>

## 📄 License

```text
Copyright (C) 2026 lingyicute <li@92li.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

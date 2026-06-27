<h1 align="center">Voxel Engine</h1>
<p align="center"><em>Dogfood Voxel Engine written in Olive</em></p>

<div align="center">

![swappy-20241017-160041](https://github.com/user-attachments/assets/85268e26-e9ef-4946-9bf0-47c21ab15bb0)

</div>

<p align="center">
  <a href="https://github.com/vinceswu/voxel-engine/stargazers">
    <img src="https://img.shields.io/github/stars/vinceswu/voxel-engine?style=flat-square">
  </a>
  <a href="https://github.com/vinceswu/voxel-engine/issues">
    <img src="https://img.shields.io/github/issues/vinceswu/voxel-engine?style=flat-square">
  </a>
  <a href="https://github.com/vinceswu/voxel-engine/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/vinceswu/voxel-engine?style=flat-square">
  </a>
  <a href="https://github.com/ecnivslabs/olive">
    <img src="https://img.shields.io/badge/language-Olive-informational?style=flat-square">
  </a>
</p>

## Overview

A voxel engine written in [Olive](https://github.com/ecnivslabs/olive). This is a dogfood project for the language, using it to build something non-trivial that touches structs, references, FFI, math, and real-time rendering.

Olive handles all the game logic. Rendering goes through pygame and ModernGL via `import py`. Noise generation is a native Olive implementation of OpenSimplex2 (no Python noise libraries needed).

## Prerequisites

- **Olive >= 0.3.9** - see installation below
- **Python 3.x** - with dependencies from `requirements.txt`

## Controls

#### Movement

| Input | Action |
|-------|--------|
| W / A / S / D | Move forward / left / backward / right |
| Space | Jump |
| Space (double-tap) | Toggle flying |
| Left Shift | Sprint (ground) / speed boost (flying) |
| Left Ctrl | Descend (flying) / sneak (ground) |
| Mouse | Look around |
| `\` | Toggle noclip (free camera, no collision) |

#### Block Interaction

| Input | Action |
|-------|--------|
| Left Click | Remove targeted block (hold to break) |
| Right Click | Place selected block |
| 1-7 | Select block type (Sand / Grass / Dirt / Stone / Snow / Leaves / Wood) |
| Scroll Wheel | Cycle block type |

#### Other

| Input | Action |
|-------|--------|
| Escape | Quit |
| F12 | Save screenshot |

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ecnivs/voxel-engine.git
cd voxel-engine
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Olive:

   **Linux / macOS:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/ecnivslabs/olive/master/install.sh | sh
   ```

   **Windows:** download from the [releases page](https://github.com/ecnivslabs/olive/releases/latest)
4. Run:
```bash
pit run
```

## What it exercises in Olive

- **Structs** with mutable and immutable references (`&mut`, `&`)
- **Python interop** (`import py`) for pygame, moderngl, glm, Pillow
- **Native math** - 727-line OpenSimplex2 noise implementation
- **Const expressions** evaluated at compile time
- **Tuple returns and destructuring**
- **Manual memory layout** - packed vertex data (6b pos + 8b voxel + 3b face + 2b AO + 1b flip per uint32 vertex)

#### *I'd appreciate any feedback or code reviews you might have!*

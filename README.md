<h1 align="center">Voxel Engine</h1>
<p align="center"><em>Voxel renderer with pygame</em></p>

<div align="center">

![swappy-20241017-160041](https://github.com/user-attachments/assets/85268e26-e9ef-4946-9bf0-47c21ab15bb0)

</div>

<p align="center">
  <a href="https://github.com/ecnivs/voxel-engine/stargazers">
    <img src="https://img.shields.io/github/stars/ecnivs/voxel-engine?style=flat-square">
  </a>
  <a href="https://github.com/ecnivs/voxel-engine/issues">
    <img src="https://img.shields.io/github/issues/ecnivs/voxel-engine?style=flat-square">
  </a>
  <a href="https://github.com/ecnivs/voxel-engine/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/ecnivs/voxel-engine?style=flat-square">
  </a>
</p>

## Overview

A voxel engine written in [Olive](https://github.com/olive-language/olive). This is a dogfood project for the language, using it to build something non-trivial that touches structs, references, FFI, math, and real-time rendering.

Olive handles all the game logic. Rendering goes through pygame and moderngl via `import py`. Noise generation is a native Olive implementation of OpenSimplex2 (no Python noise libraries needed).


## Prerequisites
* Olive >= 0.1.21
* Python 3.x (with dependencies in `requirements.txt`)

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
* **Linux / macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/olive-language/olive/master/install.sh | sh
```
* **Windows:** download from the [releases page](https://github.com/olive-language/olive/releases/latest).

4. Run the Software:
```bash
pit run
```

## Controls

| Key | Action |
|-----|--------|
| W/A/S/D | Move |
| Space | Up |
| Left Ctrl | Down |
| Left Shift | Sprint |
| Mouse | Look |
| F12 | Screenshot |
| Escape | Quit |

## What it exercises in Olive

- Structs with mutable and immutable references (`&mut`, `&`)
- Python interop (`import py`) for pygame, moderngl, numpy, glm
- Native math-heavy code (727-line OpenSimplex2 noise)
- Const expressions evaluated at compile time
- Tuple returns and destructuring
- Manual memory layout awareness (packed vertex data for GPU)

#### *I'd appreciate any feedback or code reviews you might have!*

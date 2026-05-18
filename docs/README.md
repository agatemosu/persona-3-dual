# Persona 3 Dual

A Nintendo DS demake of **Persona 3**, developed in C++ using devkitPro. This project is a personal deep-dive into embedded systems and low-level graphics programming, building a game engine from scratch without external game libraries.

The name is a nod to the online joke about a DS version of Persona 3 called "Persona 3 Dual".

![Stars](https://img.shields.io/github/stars/TheBossT910/persona-3-dual?style=flat-square&color=gold)
![Forks](https://img.shields.io/github/forks/TheBossT910/persona-3-dual?style=flat-square&color=blue)
![Last Commit](https://img.shields.io/github/last-commit/TheBossT910/persona-3-dual?style=flat-square&color=green)
![License](https://img.shields.io/github/license/TheBossT910/persona-3-dual?style=flat-square)

[![C++](https://img.shields.io/badge/C++-%2300599C.svg?logo=c%2B%2B&logoColor=white)](#)
![Platform](https://img.shields.io/badge/platform-Nintendo%20DS-red?style=flat-square)
![Toolchain](https://img.shields.io/badge/toolchain-devkitPro-orange?style=flat-square)
![Emulator](https://img.shields.io/badge/emulator-melonDS-purple?style=flat-square)
[![Blender](https://img.shields.io/badge/Blender-%23F5792A.svg?logo=blender&logoColor=white)](#)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](#)

[![Discord](https://img.shields.io/discord/1498850477545357482?label=Discord&logo=discord&style=flat-square&color=5865F2)](https://discord.gg/Xtmu76PveV)

### Want to help? Join the [Discord!](https://discord.gg/Xtmu76PveV) Any help, big or small, would be greatly appreciated!


<img width="444" height="519" alt="20260417_231005" src="https://github.com/user-attachments/assets/8dd225c8-f3eb-4b80-8ec4-feb381e4b71d" />

---

## Screenshots

| Home | Menu | Iwatodai Dorm |
|------|------|----------------------|
| ![Home](https://github.com/user-attachments/assets/735128dd-a5aa-403f-8d94-748d6294e27c) | ![Menu](https://github.com/user-attachments/assets/72eb8264-9e56-4666-84a9-07bfe96a0a78) | ![Dorm](https://github.com/user-attachments/assets/dad1562b-67ae-4566-9d04-f2a9966ba916) |


| BASE | FES | PORTABLE |
|------|-----|----------|
| <video src="https://github.com/user-attachments/assets/cfaeb394-f1cc-44f6-816e-4dc9f419216c" width="256"></video> | <video src="https://github.com/user-attachments/assets/561caee7-b622-45d1-82e9-d471d7e32427" width="256"></video> | <video src="https://github.com/user-attachments/assets/3cfd68d3-bde8-4238-8c83-58c0620a0dcd" width="256"></video> |


---

## Technical Details

| | |
|---|---|
| **Platform** | Nintendo DS |
| **CPU** | ARM9 (main) / ARM7 (sound/system) |
| **Toolchain** | devkitPro (devkitARM + libnds) |
| **Language** | C++, Python |
| **Emulator** | melonDS |

---

## Developer Setup

### 1. Install System Dependencies

**Windows:**
1. Install [devkitPro](https://devkitpro.org/wiki/Getting_Started) using the official graphical installer (ensure `nds-dev` is checked).
2. Install Python 3 from the [official website](https://www.python.org/downloads/) (check "Add Python to PATH" during install).
3. Install FFmpeg: open Command Prompt or PowerShell and run `winget install ffmpeg`.
4. Install mtools: `winget install mtools`
5. Install [melonDS](https://melonds.kuribo64.net/downloads.php) (and optionally add melonDS to PATH for debugger setup).

**macOS:**
1. Install [devkitPro](https://devkitpro.org/wiki/Getting_Started) via the official pacman pkg.
2. Install Python, FFmpeg, and mtools using Homebrew:
   `brew install python ffmpeg mtools`
3. Install [melonDS](https://melonds.kuribo64.net/downloads.php).

**Linux (Ubuntu/Debian):**
1. Install devkitPro by following the [Unix-like platforms guide](https://devkitpro.org/wiki/Getting_Started#Unix-like_platforms).
2. Install Python, FFmpeg, and mtools:
   `sudo apt update && sudo apt install python3 python3-venv ffmpeg mtools`
3. Install [melonDS](https://melonds.kuribo64.net/downloads.php).

### 2. Setup the Project
Once the system tools are installed, open your terminal, clone the repo, navigate to the project folder, and set up the Python environment:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/requirements.txt
```

You can then build by running `make clean && make` in the project folder. This will compile the ROM **and** automatically generate a `sdcard.img` FAT32 SD card image containing all required game data.

---

## Running the Game

The game requires FAT filesystem support to load assets at runtime. Currently, we only support:

- **[melonDS](https://melonds.kuribo64.net/downloads.php)** (multiplatform emulator)
- **Real DS / DSi / 3DS hardware** via [TWiLight Menu++](https://wiki.ds-homebrew.com/twilightmenu/)

> NOTE: Other flashcard launchers may work, but are untested

### melonDS (Emulator)

1. Build the project with `make` - this produces both `persona-3-dual.nds` and `sdcard.img`.
2. In melonDS, go to **Settings → DLDI** and enable DLDI.
3. Set the SD card image path to the generated `sdcard.img`.
> **Do NOT enable "Sync SD card to folder"**. This will wipe the contents of the folder.

Now, you can open melonDS and load the `persona-3-dual.nds` ROM!

### Real Hardware (DS / DSi / 3DS)

Requires [TWiLight Menu++](https://wiki.ds-homebrew.com/twilightmenu/) with DLDI patching enabled.

1. In TWiLight Menu++ settings, ensure **DLDI access** is set to **ARM9** & the **Game Loader** is set to **nds-bootstrap**
2. On your SD card, navigate to your `/roms/nds/` folder (or equivalent).
3. Copy `persona-3-dual.nds` and the entire `/data` folder into that directory:
   ```
   /roms/nds/
   ├── persona-3-dual.nds
   └── data/
       ├── music/
       ├── video/
       └── ...
   ```
4. Launch the game through TWiLight Menu++ as normal.

---

## Roadmap

See the [Project Board](https://github.com/users/TheBossT910/projects/2) for current progress and open issues.

### ✅ Major Completed Features

- [x] Intro sequence with animated backgrounds and sprites
- [x] Disclaimers screen
- [x] Main menu with interactive option selector
- [x] 3D environment rendering with UV-mapped textures
- [x] Basic camera controls
- [x] Character model + movement controls
- [x] Collision + interaction detection
- [x] Dialogue system with branching, portraits, and scrollable history
- [x] Auto word-wrap + Markdown → header dialogue generator
- [x] Music/SFX playback (PCM streaming via FAT, loop points, Maxmod SFX)
- [x] Video playback (8-bit, 15fps, interleaved audio+video, ring buffer)
- [x] Custom intro video (Persona 3 Dual logo)
- [x] Automated asset conversion pipeline (integrated into `make`)
- [x] Character walk animation + AnimationController
- [x] 3D environment & model tooling
- [x] Automated dialogue generation pipeline
- [x] Basic battle system
- [x] Basic collision/mapping system
- [x] Basic menu system

---

### 🎯 Milestone 1 - Playable Demo

The goal of Milestone 1 is a polished, presentable demo showcasing core scenes and interactions.

#### 3D & Environments

- [ ] Fix Iwatodai Dorm (source correct model) and Iwatodai Streets view
  - [ ] Model trimming & billboarding
  - [ ] Fixed camera views
  - [ ] Correct player positioning & scale
  - [ ] Collision mapping
- [ ] Add Gekkoukan High School interior (entrance area)
- [ ] Replace Kotone with Makoto model
  - [ ] Correct animations properly mapped to new model
  - [ ] Reduce poly count while preserving textures and animation accuracy
- [ ] Create the move-in intro sequence (Makoto arrives at the dorm)
  - [ ] Script events up to move-in
  - [ ] Add Gekkoukan section once the environment model is ready

#### UI

- [x] World UI - calendar and date display (top-right corner / sub-screen)
- [ ] Battle UI - console-style layout using `BaseMenu` (similar to PauseMenu/MainMenu)
- [ ] Dialogue UI - custom per-environment background (dorm, outdoors, etc.) replacing the black backdrop

#### Engine

- [ ] Stair support - character height changes when traversing stairs
- [ ] Dummy battle zone with placeholder enemy encounter
- [ ] Basic NPCs (billboard or 3D) with branching dialogue interactions

#### Misc
- [ ] Ship with a single intro video only (reduces ROM size)
- [ ] Ship with a single music zone only (reduces ROM size)

---

## Star History

<a href="https://www.star-history.com/?repos=TheBossT910%2Fpersona-3-dual&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=TheBossT910/persona-3-dual&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=TheBossT910/persona-3-dual&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=TheBossT910/persona-3-dual&type=date&legend=top-left" />
 </picture>
</a>

---

## Inspiration

Based on the **Persona 3** series of games (OG, FES, Portable, Reload), and inspired by the **Persona 3 Dual** online joke.

*This is a fan project and is not affiliated with or endorsed by Atlus or Sega.*

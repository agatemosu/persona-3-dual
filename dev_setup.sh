#!/bin/bash

MISSING=0

# --- make ---
if ! command -v make &>/dev/null; then
    echo '[INSTALL] make not found, installing...'
    sudo apt-get update -qq && sudo apt-get install -y make
    MISSING=1
else
    echo '[OK] make'
fi

# --- python3 ---
if ! command -v python3 &>/dev/null; then
    echo '[INSTALL] python3 not found, installing...'
    sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip python3-venv
    MISSING=1
else
    echo '[OK] python3'
fi

# --- python venv --
if [ ! -f ~/.venv/bin/python3 ]; then
    echo '[INSTALL] Python venv not found, creating at ~/.venv ...'
    python3 -m venv ~/.venv
    MISSING=1
else
    echo '[OK] ~/.venv'
fi

# --- ffmpeg ---
if ! command -v ffmpeg &>/dev/null; then
    echo '[INSTALL] ffmpeg not found, installing...'
    sudo apt-get update -qq && sudo apt-get install -y ffmpeg
    MISSING=1
else
    echo '[OK] ffmpeg'
fi

# --- devkitARM ---
if [ -z "$DEVKITARM" ] && [ ! -d /opt/devkitpro/devkitARM ]; then
    echo '[INSTALL] devkitARM not found, installing devkitPro...'
    wget -q https://apt.devkitpro.org/install-devkitpro-pacman
    chmod +x install-devkitpro-pacman
    sudo ./install-devkitpro-pacman
    rm install-devkitpro-pacman
    sudo dkp-pacman -S --noconfirm nds-dev
    echo 'export DEVKITPRO=/opt/devkitpro' >> ~/.bashrc
    echo 'export DEVKITARM=/opt/devkitpro/devkitARM' >> ~/.bashrc
    echo 'export PATH=$PATH:$DEVKITPRO/tools/bin:$DEVKITARM/bin' >> ~/.bashrc
    MISSING=1
else
    echo '[OK] devkitARM'
fi

# --- grit ---
if ! command -v grit &>/dev/null; then
    echo '[INSTALL] grit not found, installing...'
    sudo dkp-pacman -S --noconfirm grit 2>/dev/null || sudo apt-get install -y grit 2>/dev/null || true
    MISSING=1
else
    echo '[OK] grit'
fi

# Set DEVKITARM if not already in env
if [ -z "$DEVKITARM" ] && [ -d /opt/devkitpro/devkitARM ]; then
    export DEVKITPRO=/opt/devkitpro
    export DEVKITARM=/opt/devkitpro/devkitARM
    export PATH=$PATH:$DEVKITPRO/tools/bin:$DEVKITARM/bin
fi

if [ "$MISSING" = '1' ]; then
    echo ''
    echo '[DONE] Dependencies installed.'
    source ~/.bashrc 2>/dev/null || true
fi

if [ -n "$1" ]; then
    PROJECT_WSL="$1"
elif [ -n "${BASH_SOURCE[0]}" ] && [ "${BASH_SOURCE[0]}" != "/tmp/dev_setup.sh" ]; then
    PROJECT_WSL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elsehhehe
    WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')
    PROJECT_WSL="/mnt/c/Users/${WIN_USER}/Documents/Persona-3-Dual"
fi

if [ ! -d "$PROJECT_WSL" ]; then
    echo "[ERROR] Project directory not found: $PROJECT_WSL"
    echo "        Place dev_setup.sh in the project folder or pass the path as an argument."
    exec bash
fi

cd "$PROJECT_WSL"

echo ''
echo "[PROJECT] $PROJECT_WSL"
echo ''

exec bash

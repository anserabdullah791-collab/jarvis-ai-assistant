#!/bin/bash
# JARVIS AI Assistant - Auto Installer for macOS
# Run this in Terminal to install and start JARVIS automatically

echo ""
echo "============================================"
echo "     J.A.R.V.I.S - AI ASSISTANT"
echo "     Auto Installer for macOS"
echo "============================================"
echo ""

# Step 1: Check Python3
echo "[1/4] Checking Python3..."
if ! command -v python3 &> /dev/null; then
    echo "  Python3 not found. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "  Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
    if ! command -v python3 &> /dev/null; then
        echo "  [ERROR] Python3 installation failed."
        echo "  Please install manually from: https://www.python.org/downloads/"
        read -p "Press Enter to exit"
        exit 1
    fi
fi
echo "  Python3 found: $(python3 --version)"
echo ""

# Step 2: Check pip and install dependencies
echo "[2/4] Installing dependencies (flask, requests)..."
pip3 install flask requests -q 2>/dev/null || pip3 install --user flask requests -q 2>/dev/null
echo "  Dependencies installed."
echo ""

# Step 3: Download JARVIS
echo "[3/4] Downloading JARVIS from GitHub..."
JARVIS_DIR="$HOME/Desktop/JARVIS"

if [ -d "$JARVIS_DIR" ]; then
    echo "  JARVIS folder already exists. Updating..."
    cd "$JARVIS_DIR" && git pull -q 2>/dev/null
else
    git clone -q https://github.com/anserabdullah791-collab/jarvis-ai-assistant.git "$JARVIS_DIR" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  git not found. Downloading directly..."
        mkdir -p "$JARVIS_DIR"
        curl -sL "https://raw.githubusercontent.com/anserabdullah791-collab/jarvis-ai-assistant/main/jarvis.py" -o "$JARVIS_DIR/jarvis.py"
    fi
fi

if [ ! -f "$JARVIS_DIR/jarvis.py" ]; then
    echo "  [ERROR] Could not download JARVIS files."
    echo "  Try manually downloading from: https://github.com/anserabdullah791-collab/jarvis-ai-assistant"
    read -p "Press Enter to exit"
    exit 1
fi

echo "  JARVIS downloaded to: $JARVIS_DIR"
echo ""

# Step 4: Start JARVIS
echo "[4/4] Starting JARVIS..."
echo ""
echo "============================================"
echo "  JARVIS is ONLINE, sir!"
echo "  Browser will open automatically."
echo "  http://localhost:7654"
echo "  Press Ctrl+C to shut down."
echo "============================================"
echo ""

cd "$JARVIS_DIR"
python3 jarvis.py

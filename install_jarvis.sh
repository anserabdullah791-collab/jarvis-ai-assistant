#!/bin/bash
echo ""
echo "============================================"
echo "     J.A.R.V.I.S v4.0 - AI ASSISTANT"
echo "     Code + GitHub + Claude + Desktop"
echo "============================================"
echo ""
echo "[1/4] Checking Python3..."
if ! command -v python3 &> /dev/null; then
    echo "  Python3 not found. Installing..."
    if ! command -v brew &> /dev/null; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
fi
echo "  Python3: $(python3 --version)"
echo ""
echo "[2/4] Installing dependencies..."
pip3 install flask requests -q 2>/dev/null || pip3 install --user flask requests -q 2>/dev/null
echo "  Done."
echo ""
echo "[3/4] Downloading JARVIS v4.0..."
JARVIS_DIR="$HOME/Desktop/JARVIS"
if [ -d "$JARVIS_DIR" ]; then
    cd "$JARVIS_DIR" && git pull -q 2>/dev/null
else
    git clone -q https://github.com/anserabdullah791-collab/jarvis-ai-assistant.git "$JARVIS_DIR" 2>/dev/null || {
        mkdir -p "$JARVIS_DIR"
        curl -sL "https://raw.githubusercontent.com/anserabdullah791-collab/jarvis-ai-assistant/main/jarvis.py" -o "$JARVIS_DIR/jarvis.py"
    }
fi
echo "  Saved to: $JARVIS_DIR"
echo ""
echo "[4/4] Starting JARVIS..."
echo ""
echo "============================================"
echo "  JARVIS v4.0 is ONLINE, sir!"
echo "  60+ skills: Code, GitHub, Claude, Desktop"
echo "  Voice: macOS native (say command)"
echo "  Say 'JARVIS' then your command"
echo "============================================"
echo ""
cd "$JARVIS_DIR"
python3 jarvis.py

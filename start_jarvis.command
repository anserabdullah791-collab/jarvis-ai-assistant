#!/bin/bash
# JARVIS - One Click Start for macOS
# Double-click this file to launch JARVIS

echo "============================================"
echo "     J.A.R.V.I.S - AI ASSISTANT"
echo "     Starting up, sir..."
echo "============================================"
echo ""

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed!"
    echo "Install from: https://www.python.org/downloads/"
    echo "Or run: brew install python"
    read -p "Press Enter to exit"
    exit 1
fi

echo "Found: $(python3 --version)"

# Install dependencies
echo "Installing dependencies..."
pip3 install flask requests -q

# Check file
if [ ! -f "jarvis.py" ]; then
    echo "[ERROR] jarvis.py not found!"
    echo "Download from: https://github.com/anserabdullah791-collab/jarvis-ai-assistant"
    read -p "Press Enter to exit"
    exit 1
fi

echo ""
echo "============================================"
echo "  JARVIS is ONLINE, sir!"
echo "  Browser opening to: http://localhost:7654"
echo "  Click the mic icon to speak"
echo "  Or type your commands"
echo "  Press Ctrl+C to shut down JARVIS"
echo "============================================"
echo ""

# Run JARVIS (it opens browser automatically)
python3 jarvis.py

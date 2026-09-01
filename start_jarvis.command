#!/bin/bash
echo "============================================"
echo "     J.A.R.V.I.S v3.0 - AI ASSISTANT"
echo "     Voice + Desktop Control + Auto-Listen"
echo "============================================"
echo ""
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not installed!"
    echo "Install from: https://www.python.org/downloads/"
    read -p "Press Enter to exit"
    exit 1
fi
echo "Found: $(python3 --version)"
pip3 install flask requests -q
if [ ! -f "jarvis.py" ]; then
    echo "[ERROR] jarvis.py not found!"
    echo "Download from: https://github.com/anserabdullah791-collab/jarvis-ai-assistant"
    read -p "Press Enter to exit"
    exit 1
fi
echo ""
echo "============================================"
echo "  JARVIS v3.0 is ONLINE, sir!"
echo "  Voice: macOS native (say command)"
echo "  Say 'JARVIS' then your command"
echo "  Auto-listening is ON by default"
echo "============================================"
echo ""
python3 jarvis.py

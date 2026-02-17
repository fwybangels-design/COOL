#!/bin/bash
# Launch script for Re-Mass DM Control Panel

echo "═══════════════════════════════════════════════════════════"
echo "  Re-Mass DM Control Panel"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3 first."
    exit 1
fi

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: tkinter is not installed!"
    echo ""
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  macOS: brew install python-tk@3.9"
    exit 1
fi

# Check if discord.py is installed
python3 -c "import discord" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: discord.py is not installed!"
    echo "Installing discord.py..."
    pip3 install discord.py
fi

echo "Starting Re-Mass DM Control Panel..."
echo ""

# Launch the panel
python3 remassdm_panel.py

echo ""
echo "Panel closed."

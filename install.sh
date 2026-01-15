#!/bin/bash
# Installation script for SarScope

echo "╔═══════════════════════════════════════════╗"
echo "║      SarScope Installation Script         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║   ✓ Installation Complete!                ║"
echo "║                                           ║"
echo "║   To activate the environment, run:       ║"
echo "║   source venv/bin/activate                ║"
echo "║                                           ║"
echo "║   To start SarScope, run:                 ║"
echo "║   python sarscope/main.py                 ║"
echo "╚═══════════════════════════════════════════╝"

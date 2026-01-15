@echo off
REM Installation script for SarScope (Windows)

echo ╔═══════════════════════════════════════════╗
echo ║      SarScope Installation Script         ║
echo ╚═══════════════════════════════════════════╝
echo.

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✓ Python version: %python_version%

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ╔═══════════════════════════════════════════╗
echo ║   ✓ Installation Complete!                ║
echo ║                                           ║
echo ║   To activate the environment, run:       ║
echo ║   venv\Scripts\activate.bat                ║
echo ║                                           ║
echo ║   To start SarScope, run:                 ║
echo ║   python sarscope/main.py                 ║
echo ╚═══════════════════════════════════════════╝
pause

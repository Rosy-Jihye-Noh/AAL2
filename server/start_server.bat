@echo off
chcp 65001 >nul
cd /d %~dp0
echo Starting Flask Server...
echo.
python main.py
pause


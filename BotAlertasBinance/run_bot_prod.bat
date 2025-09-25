@echo off
setlocal
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)
python bot_alerts_binance.py
endlocal
@echo off
setlocal

REM Muda para a pasta onde este .bat está (evita problemas de caminho)
cd /d "%~dp0"

REM Verifica e ativa o venv (Windows)
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo AVISO: venv\\Scripts\\activate.bat nao encontrado em "%~dp0"
    echo Verifique se o venv existe e se o nome da pasta esta correto.
)

REM Executa o bot
python bot_alerts_binance.py

pause
endlocal
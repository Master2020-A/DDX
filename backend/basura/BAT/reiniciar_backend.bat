@echo off
echo ========================================
echo REINICIANDO BACKEND DDX
echo ========================================
echo.

echo Deteniendo procesos de uvicorn...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul

echo.
echo Esperando 2 segundos...
timeout /t 2 /nobreak >nul

echo.
echo Iniciando backend...
cd /d C:\Users\Master\Documents\DDX\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

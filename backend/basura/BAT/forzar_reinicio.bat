@echo off
echo ========================================
echo FORZANDO REINICIO COMPLETO DEL BACKEND
echo ========================================
echo.

echo 1. Matando todos los procesos Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul

echo.
echo 2. Esperando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo 3. Limpiando cache de Python...
cd /d C:\Users\Master\Documents\DDX\backend
if exist __pycache__ rmdir /s /q __pycache__
if exist app\__pycache__ rmdir /s /q app\__pycache__
if exist app\services\__pycache__ rmdir /s /q app\services\__pycache__
if exist app\api\__pycache__ rmdir /s /q app\api\__pycache__

echo.
echo 4. Iniciando backend limpio...
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8612

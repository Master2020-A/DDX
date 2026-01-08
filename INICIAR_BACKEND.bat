@echo off
echo ========================================
echo   INICIANDO BACKEND DDX
echo ========================================
echo.

cd /d C:\Users\Master\Documents\DDX\backend

echo Verificando puerto 8612...
netstat -ano | findstr ":8612" > nul
if %errorlevel% equ 0 (
    echo [ADVERTENCIA] El puerto 8612 ya esta en uso
    echo.
    echo Deseas detener el proceso existente? (S/N)
    set /p respuesta=
    if /i "%respuesta%"=="S" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8612"') do (
            echo Deteniendo proceso %%a...
            taskkill /F /PID %%a
        )
        timeout /t 2 /nobreak > nul
    )
)

echo.
echo Iniciando servidor FastAPI en puerto 8612...
echo.
echo IMPORTANTE: Busca estas lineas en los logs:
echo   - Router 'app.api.n8n' cargado en /api/n8n
echo   - Router 'app.api.n8n_workflows' cargado en /api/n8n/workflows
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8612

pause

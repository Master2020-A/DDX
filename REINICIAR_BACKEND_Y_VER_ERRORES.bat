@echo off
echo ========================================
echo   REINICIANDO BACKEND DDX CON LOGS
echo ========================================
echo.

cd /d C:\Users\Master\Documents\DDX\backend

echo Deteniendo procesos de Python en puerto 8612...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8612"') do (
    echo Deteniendo proceso %%a...
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak > nul

echo.
echo Iniciando backend con logs detallados...
echo BUSCA ESTAS LINEAS:
echo   - Router 'app.api.n8n' cargado en /api/n8n
echo   - Router 'app.api.n8n_workflows' cargado en /api/n8n/workflows
echo.
echo Si NO aparecen, busca errores con "Error cargando router 'app.api.n8n'"
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8612

pause

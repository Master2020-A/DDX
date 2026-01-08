@echo off
echo ========================================
echo INICIANDO SERVIDOR BACKEND - DDX
echo ========================================
echo.
echo Puerto: 8612
echo URL: http://localhost:8612
echo Docs: http://localhost:8612/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

python -m uvicorn app.main:app --reload --port 8612

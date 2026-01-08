@echo off
echo ================================================================================
echo INICIANDO BACKEND - SISTEMA DDX
echo ================================================================================
echo.
echo Puerto: 8612
echo API Docs: http://localhost:8612/docs
echo.

REM Activar entorno conda
call conda activate ddx

REM Iniciar servidor
echo Iniciando servidor FastAPI...
echo.
uvicorn app.main:app --reload --port 8612 --host 0.0.0.0

pause

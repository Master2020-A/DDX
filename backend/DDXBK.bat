@echo off
echo ========================================
echo SISTEMA DE DIAGNOSTICO MÉDICO CON IA
echo (Con pestanas laterales)
echo ========================================
echo.


echo Activando entorno Python 3.10...
call conda activate ddx

echo.
echo Iniciando servidor...
echo.

python -m uvicorn backend.app.main:app --reload --port 8612

pause

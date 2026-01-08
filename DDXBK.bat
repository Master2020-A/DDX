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

cd backend

python -m uvicorn app.main:app --reload --port 8612

pause

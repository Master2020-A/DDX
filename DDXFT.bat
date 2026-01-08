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

cd frontend

call npm run dev

pause

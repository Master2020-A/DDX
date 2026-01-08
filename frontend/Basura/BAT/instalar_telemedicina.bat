@echo off
echo ========================================
echo INSTALACION MODULO DE TELEMEDICINA
echo ========================================
echo.

echo [1/1] Instalando dependencias frontend...
call npm install simple-peer socket.io-client

echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
echo.
echo Presiona cualquier tecla para continuar...
pause > nul

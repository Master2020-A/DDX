@echo off
echo ========================================
echo INSTALACION MODULO DE TELEMEDICINA
echo ========================================
echo.

echo [1/2] Instalando dependencias backend...
pip install python-socketio aiofiles reportlab qrcode pillow

echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
echo.
echo Presiona cualquier tecla para continuar...
pause > nul

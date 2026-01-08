@echo off
echo ========================================
echo AGREGAR CODIGOS POSTALES A LA BD
echo ========================================
echo.
echo NOTA: Asegurate de tener el entorno virtual activado
echo       Debes ver (ddx) al inicio de la linea de comandos
echo.
pause

echo.
echo Agregando codigos postales comunes...
echo.
python agregar_codigos_postales.py

echo.
echo ========================================
echo LISTADO DE CODIGOS POSTALES
echo ========================================
echo.
python agregar_codigos_postales.py --listar

echo.
pause

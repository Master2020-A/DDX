@echo off
echo ========================================
echo AGREGAR CODIGOS POSTALES A LA BD
echo ========================================
echo.

echo Agregando codigos postales comunes...
echo.

REM Intentar con el entorno virtual activado
if exist "ddx\Scripts\python.exe" (
    echo Usando entorno virtual ddx...
    ddx\Scripts\python.exe agregar_codigos_postales.py
) else (
    echo Usando Python del sistema...
    python agregar_codigos_postales.py
)

echo.
echo ========================================
echo PRESIONA ENTER PARA VER LA LISTA
echo ========================================
pause

echo.
echo ========================================
echo LISTADO DE CODIGOS POSTALES
echo ========================================
echo.

REM Intentar con el entorno virtual activado
if exist "ddx\Scripts\python.exe" (
    ddx\Scripts\python.exe agregar_codigos_postales.py --listar
) else (
    python agregar_codigos_postales.py --listar
)

echo.
pause

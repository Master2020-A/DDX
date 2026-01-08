@echo off
cd /d "%~dp0"
echo ========================================
echo ACTUALIZAR SISTEMA DE COLONIAS
echo ========================================
echo.
echo Este script hara lo siguiente:
echo 1. Ejecutar migracion para permitir multiples colonias
echo 2. Agregar codigos con TODAS sus colonias
echo.
pause

echo.
echo ========================================
echo PASO 1: EJECUTAR MIGRACION SQL
echo ========================================
echo.

REM Intentar con el entorno virtual activado
if exist "ddx\Scripts\python.exe" (
    echo Usando entorno virtual...
    ddx\Scripts\python.exe migrations\ejecutar_migraciones.py
) else (
    echo Usando Python del sistema...
    python migrations\ejecutar_migraciones.py
)

echo.
echo ========================================
echo PASO 2: AGREGAR CODIGOS CON COLONIAS
echo ========================================
echo.
echo Agregando codigos postales con TODAS las colonias...
echo.

if exist "ddx\Scripts\python.exe" (
    ddx\Scripts\python.exe agregar_codigos_postales.py
) else (
    python agregar_codigos_postales.py
)

echo.
echo ========================================
echo COMPLETADO
echo ========================================
echo.
echo Ahora reinicia el backend:
echo uvicorn app.main:app --reload --port=8612
echo.
pause

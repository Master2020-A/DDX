@echo off
echo =========================================
echo Migracion de Workflows Avanzados
echo =========================================
echo.
echo Este script creara las tablas para:
echo - Versionado de workflows
echo - A/B Testing
echo - Loops y Subworkflows
echo.
echo =========================================
echo.

python migrar_workflows_avanzado.py

echo.
echo =========================================
echo Presiona cualquier tecla para salir...
pause > nul

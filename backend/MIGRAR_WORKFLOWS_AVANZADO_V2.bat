@echo off
echo =========================================
echo Migracion de Workflows Avanzados V2
echo =========================================
echo.
echo Este script usa psycopg2 (mas estable)
echo.
echo Creara las tablas para:
echo - Versionado de workflows
echo - A/B Testing
echo - Loops y Subworkflows
echo.
echo =========================================
echo.

python migrar_workflows_avanzado_v2.py

echo.
echo =========================================
pause

@echo off
echo ======================================================================
echo EJECUTANDO MIGRACION DEL MODULO DE INTEGRACIONES
echo ======================================================================
echo.

echo [1/2] Creando tablas...
python crear_tablas_integraciones.py
if %errorlevel% neq 0 (
    echo ERROR: Fallo al crear tablas
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] Poblando datos de prueba...
python poblar_integraciones.py
if %errorlevel% neq 0 (
    echo ERROR: Fallo al poblar datos
    pause
    exit /b %errorlevel%
)

echo.
echo ======================================================================
echo MIGRACION COMPLETADA EXITOSAMENTE
echo ======================================================================
echo.
echo El modulo de Integraciones esta listo!
echo Accede a: http://localhost:5173/integraciones
echo.
pause

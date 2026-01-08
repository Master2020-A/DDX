@echo off
echo ======================================================================
echo EJECUTANDO MIGRACION - Estudios Especiales
echo ======================================================================
echo.

echo Paso 1: Creando migracion...
alembic revision --autogenerate -m "Agregar estudios especiales (EKG, EEG, Ecografias)"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo crear la migracion
    echo Revisa los errores arriba
    pause
    exit /b 1
)

echo.
echo Paso 2: Aplicando migracion...
alembic upgrade head

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo aplicar la migracion
    echo Revisa los errores arriba
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo MIGRACION COMPLETADA EXITOSAMENTE
echo ======================================================================
echo.
echo Ahora puedes reiniciar el servidor:
echo   uvicorn app.main:app --reload --port 8612
echo.
pause

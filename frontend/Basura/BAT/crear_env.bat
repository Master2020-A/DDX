@echo off
echo ========================================
echo CREANDO ARCHIVO .env PARA FRONTEND
echo ========================================
echo.

REM Verificar si ya existe
if exist .env (
    echo [!] El archivo .env ya existe.
    echo.
    type .env
    echo.
    echo ========================================
    set /p overwrite="Deseas sobrescribirlo? (S/N): "
    if /i not "%overwrite%"=="S" (
        echo.
        echo Operacion cancelada.
        pause
        exit /b
    )
)

REM Copiar desde .env.example
if exist .env.example (
    echo Copiando desde .env.example...
    copy .env.example .env >nul
    echo.
    echo [OK] Archivo .env creado desde .env.example
) else (
    REM Crear desde cero
    echo Creando .env desde cero...
    echo VITE_API_URL=http://localhost:8612 > .env
    echo.
    echo [OK] Archivo .env creado manualmente
)

echo.
echo ========================================
echo CONTENIDO DEL ARCHIVO .env:
echo ========================================
type .env

echo.
echo ========================================
echo SIGUIENTE PASO:
echo ========================================
echo.
echo 1. Detener el frontend si esta corriendo (Ctrl+C)
echo 2. Ejecutar: npm run dev
echo 3. Probar el codigo postal en Nuevo Paciente
echo.

pause

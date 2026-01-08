@echo off
echo ============================================================
echo REPARANDO E INICIANDO BACKEND DDX
echo ============================================================
echo.

cd /d "%~dp0"

echo [1] Activando entorno virtual...
call ddx\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo.
echo [2] Reparando bcrypt...
pip uninstall bcrypt -y
pip install bcrypt==4.1.2

echo.
echo [3] Verificando bcrypt...
python -c "import bcrypt; print('OK - bcrypt version:', bcrypt.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: bcrypt no funciona correctamente
    pause
    exit /b 1
)

echo.
echo [4] Creando usuario admin (si no existe)...
python crear_admin.py

echo.
echo ============================================================
echo [5] INICIANDO BACKEND EN PUERTO 8612
echo ============================================================
echo.
echo Presiona CTRL+C para detener el servidor
echo.

uvicorn app.main:app --reload --port=8612

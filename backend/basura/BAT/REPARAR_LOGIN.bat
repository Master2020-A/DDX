@echo off
echo ============================================================
echo REPARANDO SISTEMA DE LOGIN - MIGRACION A ARGON2
echo ============================================================
echo.

cd /d "%~dp0"

echo [1] Instalando argon2-cffi...
pip install argon2-cffi
if errorlevel 1 (
    echo ERROR: No se pudo instalar argon2-cffi
    pause
    exit /b 1
)

echo.
echo [2] Migrando usuarios a argon2...
python migrar_a_argon2.py
if errorlevel 1 (
    echo ERROR: No se pudo migrar usuarios
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [OK] SISTEMA REPARADO
echo ============================================================
echo.
echo Credenciales de acceso:
echo Email:    admin@ddx.com
echo Password: Admin123!
echo.
echo Ahora puedes iniciar el backend con: INICIAR_BACKEND_FIJO.bat
echo ============================================================
echo.
pause

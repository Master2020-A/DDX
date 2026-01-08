@echo off
echo ============================================================
echo REPARANDO BCRYPT
echo ============================================================
echo.

cd /d "%~dp0"

echo [1] Activando entorno virtual...
call ddx\Scripts\activate.bat

echo.
echo [2] Desinstalando bcrypt corrupto...
pip uninstall bcrypt -y

echo.
echo [3] Limpiando cache de pip...
pip cache purge

echo.
echo [4] Instalando bcrypt 4.1.2...
pip install bcrypt==4.1.2

echo.
echo [5] Verificando instalacion...
python -c "import bcrypt; print('✓ bcrypt version:', bcrypt.__version__)"

echo.
echo ============================================================
echo REPARACION COMPLETADA
echo ============================================================
echo.
echo Ahora:
echo 1. Presiona CTRL+C en la terminal donde corre uvicorn
echo 2. Reinicia el backend: uvicorn app.main:app --reload --port=8612
echo.
pause

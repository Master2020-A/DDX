@echo off
echo ========================================
echo AI DUBBING STUDIO - INTERFAZ HTML
echo (Con pestanas laterales)
echo ========================================
echo.

if not exist "venv_py310\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado
    echo.
    echo Primero ejecuta: crear_entorno_python310.bat
    echo.
    pause
    exit /b 1
)

echo Activando entorno Python 3.10...
call venv_py310\Scripts\activate.bat

echo.
echo Iniciando servidor...
echo.

python start_html_ui.py

pause

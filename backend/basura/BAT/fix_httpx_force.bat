@echo off
echo ========================================
echo FORZANDO DOWNGRADE DE HTTPX A 0.27.0
echo ========================================
echo.

echo Desinstalando httpx actual...
pip uninstall -y httpx

echo.
echo Instalando httpx 0.27.0 (version estable)...
pip install httpx==0.27.0

echo.
echo Desinstalando httpcore actual...
pip uninstall -y httpcore

echo.
echo Instalando httpcore 1.0.5 (compatible)...
pip install httpcore==1.0.5

echo.
echo ========================================
echo VERIFICANDO INSTALACION
echo ========================================
echo.
pip show httpx
echo.
pip show httpcore

echo.
echo ========================================
echo CORRECCION COMPLETADA
echo ========================================
echo.
echo Ahora reinicia el backend con:
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8612
echo.
pause

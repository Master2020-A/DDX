@echo off
echo ========================================
echo CORRIGIENDO HTTPX PARA OPENAI 1.40.0
echo ========================================
echo.

echo Verificando versiones actuales...
pip show httpx
echo.
pip show httpcore
echo.

echo ========================================
echo INSTALANDO VERSIONES COMPATIBLES
echo ========================================
echo.

echo Instalando httpx compatible...
pip install "httpx>=0.23.0,<1.0.0" --upgrade

echo.
echo Instalando httpcore compatible...
pip install "httpcore>=0.15.0,<2.0.0" --upgrade

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

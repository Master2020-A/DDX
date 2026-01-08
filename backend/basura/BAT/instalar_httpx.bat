@echo off
echo ========================================
echo INSTALANDO HTTPX PARA API DE SEPOMEX
echo ========================================
echo.

echo Instalando httpx...
ddx\Scripts\pip.exe install httpx

echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
echo.

echo Verificando instalacion...
ddx\Scripts\pip.exe list | findstr httpx

echo.
echo ========================================
echo LISTO!
echo ========================================
echo.
echo Ahora puedes iniciar el backend:
echo   uvicorn app.main:app --reload --port=8612
echo.
pause

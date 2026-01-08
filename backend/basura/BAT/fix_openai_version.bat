@echo off
echo ========================================
echo CORRIGIENDO VERSION DE OPENAI
echo ========================================
echo.

echo Verificando version actual...
pip show openai
echo.

echo ========================================
echo INSTALANDO VERSION COMPATIBLE
echo ========================================
echo.

echo Desinstalando version actual...
pip uninstall -y openai

echo.
echo Instalando OpenAI 1.40.0 (version estable sin bug de proxies)...
pip install openai==1.40.0

echo.
echo ========================================
echo VERIFICANDO INSTALACION
echo ========================================
echo.
pip show openai
echo.

echo ========================================
echo CORRECCION COMPLETADA
echo ========================================
echo.
echo Ahora reinicia el backend con:
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8612
echo.
pause

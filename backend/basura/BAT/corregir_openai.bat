@echo off
echo ========================================
echo CORRIGIENDO VERSION DE OPENAI
echo ========================================
echo.

echo Desinstalando OpenAI 1.55.2...
pip uninstall -y openai

echo.
echo Instalando OpenAI 1.40.0 (version estable)...
pip install openai==1.40.0

echo.
echo ========================================
echo CORRECCION COMPLETADA
echo ========================================
echo.
echo Verifica la instalacion:
python -c "import openai; print(f'OpenAI version: {openai.__version__}')"
echo.
pause

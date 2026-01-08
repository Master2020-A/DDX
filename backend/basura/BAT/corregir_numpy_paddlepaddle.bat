@echo off
echo ================================================================================
echo CORRECCION: Error de NumPy con PaddlePaddle
echo ================================================================================
echo.
echo Problema detectado: PaddlePaddle requiere NumPy 1.x pero tienes NumPy 2.x
echo Solucion: Downgrade de NumPy a version compatible
echo.
echo Ejecutando correccion...
echo.

pip install "numpy<2.0" --force-reinstall

echo.
echo ✓ NumPy downgradeado a version compatible
echo.
echo Verificando instalacion...
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
echo.
echo ================================================================================
echo CORRECCION COMPLETADA
echo ================================================================================
echo.
echo Ahora ejecuta nuevamente:
echo   python verificar_modelos_segmentacion.py
echo.
pause

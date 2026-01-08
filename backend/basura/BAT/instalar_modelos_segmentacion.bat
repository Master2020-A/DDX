@echo off
echo ================================================================================
echo INSTALACION DE MODELOS DE SEGMENTACION AVANZADA - SISTEMA DDX
echo ================================================================================
echo.

echo [1/5] Instalando LungMask (Analisis Pulmonar)...
echo Tamano aproximado: ~100MB
pip install lungmask
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar LungMask
    pause
    exit /b 1
)
echo ✓ LungMask instalado correctamente
echo.

echo [2/5] Instalando TotalSegmentator (104 Estructuras)...
echo Tamano aproximado: ~1.5GB (modelos se descargan al primer uso)
pip install totalsegmentator
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar TotalSegmentator
    pause
    exit /b 1
)
echo ✓ TotalSegmentator instalado correctamente
echo.

echo [3/5] Instalando nnU-Net (Framework Universal)...
echo Tamano aproximado: Variable segun modelos
pip install nnunetv2
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar nnU-Net
    pause
    exit /b 1
)
echo ✓ nnU-Net instalado correctamente
echo.

echo [4/5] Instalando PaddlePaddle y PaddleSeg...
echo Tamano aproximado: ~500MB
pip install paddlepaddle==2.5.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Error instalando PaddlePaddle desde mirror chino
    echo Intentando instalacion desde PyPI oficial...
    pip install paddlepaddle
)
pip install paddleseg
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar PaddleSeg
    pause
    exit /b 1
)
echo ✓ PaddleSeg instalado correctamente
echo.

echo [5/5] Verificando instalaciones...
python verificar_modelos_segmentacion.py
echo.

echo ================================================================================
echo INSTALACION COMPLETADA
echo ================================================================================
echo.
echo Modelos instalados:
echo   ✓ LungMask
echo   ✓ TotalSegmentator
echo   ✓ nnU-Net
echo   ✓ PaddleSeg
echo.
echo NOTAS IMPORTANTES:
echo   - Los modelos se descargaran automaticamente al primer uso
echo   - TotalSegmentator descargara ~1.5GB adicionales
echo   - GPU CUDA es opcional (ver instrucciones abajo)
echo.
echo Para instalar GPU CUDA (opcional - mejora velocidad):
echo   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
echo.
pause

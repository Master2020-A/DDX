@echo off
echo ================================================================================
echo REINSTALACION DE MODELOS - Post-NumPy Fix
echo ================================================================================
echo.
echo NumPy fue downgradeado a 1.x
echo Ahora necesitamos reinstalar todos los modelos para que se recompilen
echo con la nueva version de NumPy.
echo.
pause

echo.
echo [1/6] Reinstalando LungMask...
pip uninstall lungmask -y
pip install lungmask
echo.

echo [2/6] Reinstalando TorchIO...
pip uninstall torchio -y
pip install torchio
echo.

echo [3/6] Reinstalando TotalSegmentator...
pip uninstall totalsegmentator -y
pip install totalsegmentator
echo.

echo [4/6] Reinstalando nnU-Net...
pip uninstall nnunetv2 -y
pip install nnunetv2
echo.

echo [5/6] Reinstalando MONAI...
pip uninstall monai -y
pip install "monai[all]"
echo.

echo [6/6] Reinstalando PaddlePaddle y PaddleSeg...
pip uninstall paddlepaddle paddleseg -y
pip install paddlepaddle paddleseg
echo.

echo ================================================================================
echo REINSTALACION COMPLETADA
echo ================================================================================
echo.
echo Verificando instalacion...
python verificar_modelos_segmentacion.py
echo.
pause

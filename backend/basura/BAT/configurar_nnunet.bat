@echo off
echo ================================================================================
echo CONFIGURACION DE VARIABLES DE ENTORNO - nnU-Net
echo ================================================================================
echo.
echo nnU-Net requiere 3 variables de entorno para funcionar:
echo   1. nnUNet_raw - Datos sin procesar
echo   2. nnUNet_preprocessed - Datos preprocesados
echo   3. nnUNet_results - Resultados de modelos
echo.

set NNUNET_BASE=%USERPROFILE%\nnUNet_data

echo Creando directorios en: %NNUNET_BASE%
mkdir "%NNUNET_BASE%\nnUNet_raw" 2>nul
mkdir "%NNUNET_BASE%\nnUNet_preprocessed" 2>nul
mkdir "%NNUNET_BASE%\nnUNet_results" 2>nul

echo.
echo Configurando variables de entorno (solo para esta sesion)...
set nnUNet_raw=%NNUNET_BASE%\nnUNet_raw
set nnUNet_preprocessed=%NNUNET_BASE%\nnUNet_preprocessed
set nnUNet_results=%NNUNET_BASE%\nnUNet_results

echo.
echo ✓ Variables configuradas:
echo   nnUNet_raw=%nnUNet_raw%
echo   nnUNet_preprocessed=%nnUNet_preprocessed%
echo   nnUNet_results=%nnUNet_results%
echo.

echo ================================================================================
echo CONFIGURACION TEMPORAL COMPLETADA
echo ================================================================================
echo.
echo NOTA: Estas variables solo funcionan en esta ventana de CMD.
echo.
echo Para hacerlas permanentes:
echo   1. Buscar "Variables de entorno" en Windows
echo   2. Agregar las 3 variables del sistema con los valores mostrados arriba
echo.
echo O ejecutar este comando (requiere permisos de administrador):
echo   setx nnUNet_raw "%nnUNet_raw%"
echo   setx nnUNet_preprocessed "%nnUNet_preprocessed%"
echo   setx nnUNet_results "%nnUNet_results%"
echo.
pause

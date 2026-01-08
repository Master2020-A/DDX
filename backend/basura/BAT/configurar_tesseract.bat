@echo off
echo ========================================
echo CONFIGURANDO TESSERACT OCR
echo ========================================
echo.

echo Verificando si Tesseract esta instalado...
where tesseract >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Tesseract encontrado en PATH
    tesseract --version
) else (
    echo ⚠️ Tesseract NO encontrado en PATH
    echo.
    echo Agregando Tesseract al PATH del sistema...
    setx PATH "%PATH%;C:\Program Files\Tesseract-OCR" /M
    echo.
    echo ✅ PATH actualizado
    echo.
    echo IMPORTANTE: Cierra y vuelve a abrir la terminal para que los cambios surtan efecto
)

echo.
echo ========================================
echo VERIFICANDO INSTALACION DE PYTESSERACT
echo ========================================
echo.

python -c "import pytesseract; print('✅ pytesseract instalado')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ pytesseract no instalado
    echo Instalando pytesseract...
    pip install pytesseract
)

echo.
echo ========================================
echo CONFIGURACION COMPLETADA
echo ========================================
echo.
echo Si Tesseract no estaba en PATH, reinicia la terminal y ejecuta:
echo   tesseract --version
echo.
pause

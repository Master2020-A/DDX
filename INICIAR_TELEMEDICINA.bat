@echo off
color 0A
title Instalacion y Prueba - Modulo de Telemedicina

echo.
echo  ========================================================================
echo    MODULO DE TELEMEDICINA - INSTALACION Y CONFIGURACION
echo  ========================================================================
echo.
echo  Este script instalara y configurara el modulo de telemedicina completo
echo.
echo  Pasos:
echo    1. Instalar dependencias backend
echo    2. Instalar dependencias frontend  
echo    3. Ejecutar pruebas automaticas
echo    4. Iniciar servidores
echo.
echo  ========================================================================
echo.
pause

echo.
echo [PASO 1/4] Instalando dependencias backend...
echo ========================================================================
cd backend
call pip install python-socketio aiofiles reportlab qrcode pillow
if %errorlevel% neq 0 (
    echo ERROR: Fallo la instalacion de dependencias backend
    pause
    exit /b 1
)
echo.
echo ✓ Dependencias backend instaladas correctamente
echo.

echo.
echo [PASO 2/4] Instalando dependencias frontend...
echo ========================================================================
cd ..\frontend
call npm install simple-peer socket.io-client
if %errorlevel% neq 0 (
    echo ERROR: Fallo la instalacion de dependencias frontend
    pause
    exit /b 1
)
echo.
echo ✓ Dependencias frontend instaladas correctamente
echo.

echo.
echo [PASO 3/4] Ejecutando pruebas automaticas...
echo ========================================================================
cd ..\backend
echo.
echo Asegurate de que el servidor backend este corriendo en http://localhost:8612
echo.
choice /C SN /M "¿Esta el servidor backend corriendo?"
if errorlevel 2 (
    echo.
    echo Por favor, inicia el servidor backend primero:
    echo    cd backend
    echo    python -m uvicorn app.main:app --reload --port 8612
    echo.
    pause
    exit /b 1
)

echo.
echo Ejecutando pruebas...
python test_telemedicina.py
echo.

echo.
echo [PASO 4/4] Informacion de servidores
echo ========================================================================
echo.
echo Para iniciar los servidores, ejecuta en terminales separadas:
echo.
echo   Terminal 1 - Backend:
echo     cd backend
echo     iniciar_servidor.bat
echo.
echo   Terminal 2 - Frontend:
echo     cd frontend
echo     iniciar_servidor.bat
echo.
echo ========================================================================
echo.
echo ✓ INSTALACION COMPLETADA
echo.
echo Proximos pasos:
echo   1. Inicia ambos servidores (backend y frontend)
echo   2. Abre: http://localhost:5173/telemedicina/sala/{CONSULTA_ID}
echo   3. Acepta permisos de camara/microfono
echo   4. Prueba videollamada y chat
echo.
echo Documentacion:
echo   - GUIA_PRUEBAS_TELEMEDICINA.html (abre en navegador)
echo   - INSTALACION_TELEMEDICINA.md
echo   - MODULO_TELEMEDICINA_DOCUMENTACION.md
echo.
echo ========================================================================
echo.
pause

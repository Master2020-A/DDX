@echo off
echo ====================================
echo CONFIGURANDO PORTAL DEL PACIENTE
echo ====================================
echo.
echo Paso 1: Creando tablas...
python crear_tablas_portal.py
echo.
echo Paso 2: Poblando datos...
python poblar_portal_paciente.py
echo.
echo ====================================
echo COMPLETADO
echo ====================================
pause

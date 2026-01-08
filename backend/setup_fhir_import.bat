@echo off
echo ============================================================
echo CONFIGURACION DEL SISTEMA DE IMPORTACION FHIR
echo ============================================================
echo.

echo Paso 1: Instalando dependencias...
pip install httpx
echo.

echo Paso 2: Verificando modulos...
python -c "from app.api.fhir_import import router; print('✅ Router cargado correctamente con', len(router.routes), 'rutas')"
if %errorlevel% neq 0 (
    echo ❌ Error al cargar el router
    pause
    exit /b 1
)
echo.

echo ============================================================
echo ✅ VERIFICACION COMPLETADA
echo ============================================================
echo.
echo SIGUIENTE PASO - EJECUTAR MIGRACION DE BASE DE DATOS:
echo.
echo   psql -U ddx_user -d ddx_db -f migrations/010_add_fhir_conditions.sql
echo.
echo LUEGO REINICIAR EL SERVIDOR:
echo.
echo   uvicorn app.main:app --reload
echo.
echo ============================================================
pause

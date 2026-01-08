@echo off
echo Poblando datos...
python poblar_ahora.py > poblacion_log.txt 2>&1
echo.
echo Resultado guardado en poblacion_log.txt
type poblacion_log.txt
pause

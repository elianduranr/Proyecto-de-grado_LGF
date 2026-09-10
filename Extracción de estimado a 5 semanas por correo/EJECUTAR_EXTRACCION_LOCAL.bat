@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Extraccion de estimados semanales

set "PYTHON_EXE=..\entorno_tesis\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo Preparando entorno local de extraccion...
    where py >nul 2>nul || goto :sin_python
    py -3 -m venv entorno_extraccion
    if errorlevel 1 goto :error
    set "PYTHON_EXE=entorno_extraccion\Scripts\python.exe"
    "%PYTHON_EXE%" -m pip install selenium
    if errorlevel 1 goto :error
)

"%PYTHON_EXE%" -c "import selenium" >nul 2>nul
if errorlevel 1 (
    "%PYTHON_EXE%" -m pip install selenium
    if errorlevel 1 goto :error
)

echo.
set /p ANIOS=Escribe los anios separados por espacios [2023 2024 2025 2026]: 
if "%ANIOS%"=="" set "ANIOS=2023 2024 2025 2026"

for %%A in (%ANIOS%) do (
    echo.
    echo Procesando %%A...
    "%PYTHON_EXE%" -u descargar_estimados_selenium.py --anio %%A --remitentes --inicio 1 --hasta-mes 12 --etiqueta local_%%A
)

echo.
echo Proceso terminado. Revisa ..\Datos\Estimados semanales
pause
exit /b 0

:sin_python
echo No se encontro Python ni el entorno_tesis del proyecto.
pause
exit /b 1

:error
echo No fue posible preparar o ejecutar la extraccion.
pause
exit /b 1

@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 exit /b 1
)
.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
if errorlevel 1 exit /b 1
call npm.cmd ci --prefix frontend
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe scripts\configurar.py
if errorlevel 1 exit /b 1
pushd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
if errorlevel 1 exit /b 1
popd
echo.
echo Instalacion terminada. Ejecuta iniciar.cmd para revisar la plataforma.


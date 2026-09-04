@echo off
setlocal
set PROJECT_ROOT=%~dp0..\..
set PY=%PROJECT_ROOT%\venv\Scripts\python.exe
if not exist "%PY%" set PY=python

:loop
"%PY%" "%PROJECT_ROOT%\api\api_server.py"
echo [%date% %time%] api_server.py terminó, reiniciando en 5s...
timeout /t 5 /nobreak >nul
goto loop

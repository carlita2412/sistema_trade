@echo off
setlocal
set PROJECT_ROOT=%~dp0..\..
set PY=%PROJECT_ROOT%\venv\Scripts\python.exe
if not exist "%PY%" set PY=python

"%PY%" "%PROJECT_ROOT%\scripts\refresh_worker.py"

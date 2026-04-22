@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

if exist "%PYTHON%" (
    "%PYTHON%" -m src.app status
) else (
    python -m src.app status
)

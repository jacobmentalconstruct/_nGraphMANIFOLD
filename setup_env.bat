@echo off
setlocal

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"

if not exist "%VENV%\Scripts\python.exe" (
    python -m venv "%VENV%"
)

call "%VENV%\Scripts\activate.bat"
python -m pip install --upgrade pip
if exist "%ROOT%requirements.txt" (
    python -m pip install -r "%ROOT%requirements.txt"
)

echo Environment ready.

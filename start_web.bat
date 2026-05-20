@echo off
setlocal
cd /d "%~dp0"
set "PY="

if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY where py >nul 2>nul && set "PY=py"
if not defined PY where python >nul 2>nul && set "PY=python"

if not defined PY (
  echo Python was not found. Please install Python 3.10+ or create .venv\Scripts\python.exe.
  pause
  exit /b 1
)

"%PY%" -m workflow.web_app --host 127.0.0.1 --port 8000 --open-browser

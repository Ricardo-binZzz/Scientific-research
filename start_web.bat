@echo off
setlocal
cd /d "%~dp0"
set "PY=C:\Users\22676\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
start "" http://127.0.0.1:8000
"%PY%" -m workflow.web_app --host 127.0.0.1 --port 8000

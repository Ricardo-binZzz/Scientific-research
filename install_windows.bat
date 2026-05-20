@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Research Workflow Windows installer
echo.

set "BOOTSTRAP_PY="
if exist ".venv\Scripts\python.exe" set "BOOTSTRAP_PY=.venv\Scripts\python.exe"
if not defined BOOTSTRAP_PY where py >nul 2>nul && set "BOOTSTRAP_PY=py"
if not defined BOOTSTRAP_PY where python >nul 2>nul && set "BOOTSTRAP_PY=python"

if not defined BOOTSTRAP_PY (
  echo Python was not found. Please install Python 3.10+ from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating local virtual environment...
  rem python -m venv .venv
  "%BOOTSTRAP_PY%" -m venv .venv
  if errorlevel 1 (
    echo Failed to create .venv.
    pause
    exit /b 1
  )
)

set "APP_PY=.venv\Scripts\python.exe"
echo Verifying local web app...
"%APP_PY%" -c "import workflow.web_app"
if errorlevel 1 (
  echo The workflow.web_app module could not be imported.
  pause
  exit /b 1
)

set "ROOT_LAUNCHER=%~dp0Research Workflow Web.bat"
(
  echo @echo off
  echo cd /d "%~dp0"
  echo call start_web.bat
) > "%ROOT_LAUNCHER%"

set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%" (
  copy /Y "%ROOT_LAUNCHER%" "%DESKTOP%\Research Workflow Web.bat" >nul
  echo Desktop launcher created: %DESKTOP%\Research Workflow Web.bat
) else (
  echo Desktop folder was not found. Launcher created in the project folder.
)

echo.
echo Installation finished. Double-click "Research Workflow Web.bat" to open the web workbench.
pause

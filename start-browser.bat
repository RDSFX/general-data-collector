@echo off
REM Browser startup entry point
REM Uses Python from the virtual environment to execute the startup script

setlocal

REM Get script directory (project root)
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Python interpreter path
set PYTHON_EXE=%SCRIPT_DIR%\.venv\Scripts\python.exe

REM Startup script path
set START_SCRIPT=%SCRIPT_DIR%\scripts\start_browser.py

REM Browser configuration path
set BROWSER_CONFIG=%SCRIPT_DIR%\config\browser.toml

REM Check Python interpreter
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python interpreter not found: %PYTHON_EXE%
    echo Please ensure the virtual environment is created
    exit /b 1
)

REM Check startup script
if not exist "%START_SCRIPT%" (
    echo [ERROR] Startup script not found: %START_SCRIPT%
    exit /b 1
)

REM Check configuration file
if not exist "%BROWSER_CONFIG%" (
    echo [ERROR] Browser configuration not found: %BROWSER_CONFIG%
    exit /b 1
)

REM Execute startup script
"%PYTHON_EXE%" "%START_SCRIPT%"
exit /b %ERRORLEVEL%

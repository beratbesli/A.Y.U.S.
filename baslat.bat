@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ilk kullanim: kurulum baslatiliyor...
    call "%~dp0kurulum.bat"
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -m ayus
if errorlevel 1 pause

@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ilk kullanim: Python sanal ortami olusturuluyor...
    py -3.11 -m venv .venv
    if errorlevel 1 (
        echo Python 3.11 bulunamadi. Lutfen Python 3.11 kurun.
        pause
        exit /b 1
    )
)

echo Paketleme bagimliliklari kuruluyor...
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 (
    echo Paketleme bagimliliklari kurulamadi.
    pause
    exit /b 1
)

echo A.Y.U.S. exe olusturuluyor...
".venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm ayus.spec
if errorlevel 1 (
    echo Paketleme basarisiz.
    pause
    exit /b 1
)

echo Hazir: %~dp0dist\A.Y.U.S.exe
pause

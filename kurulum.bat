@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Python 3.11 sanal ortami olusturuluyor...
    py -3.11 -m venv .venv
    if errorlevel 1 (
        echo Sanal ortam olusturulamadi. Python 3.11 kurulu mu kontrol edin.
        pause
        exit /b 1
    )
)

echo Bagimliliklar kuruluyor...
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 (
    echo Bagimlilik kurulumu basarisiz.
    pause
    exit /b 1
)

echo Kurulum tamamlandi. Uygulamayi baslatmak icin baslat.bat dosyasini acabilirsiniz.
pause

@echo off
chcp 65001 >nul
title EGS Scrapper - Kurulum ve Calistirma

echo ==========================================
echo        EGS SCRAPPER KURULUM ARACI
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/5] Klasorler kontrol ediliyor...
if not exist "databases" mkdir "databases"
if not exist "logs" mkdir "logs"
if not exist "error_reports" mkdir "error_reports"
echo Tamam.
echo.

echo [2/5] Python kontrol ediliyor...
python --version >nul 2>nul
if errorlevel 1 (
    echo Python bulunamadi.
    echo Lutfen once Python kur.
    echo Indir: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [3/5] Pip kontrol ediliyor...
python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo Pip bulunamadi.
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [4/5] Gerekli kutuphaneler kontrol ediliyor...
python -c "import PySide6" >nul 2>nul
if errorlevel 1 (
    echo Gerekli kutuphaneler eksik. Kuruluyor...
    python -m pip install --upgrade pip
    if exist "requirements.txt" (
        python -m pip install -r requirements.txt
    ) else (
        python -m pip install PySide6
    )
    if errorlevel 1 (
        echo Kutuphane kurulumu basarisiz oldu.
        pause
        exit /b 1
    )
) else (
    echo Temel kutuphaneler zaten kurulu.
)
echo Tamam.
echo.

echo [5/5] Program baslatiliyor...
python app.py

if errorlevel 1 (
    echo.
    echo Program calisirken bir hata olustu.
    echo logs klasorundeki log dosyalarini kontrol et.
    echo Yardim menusu altindaki Log Goruntuleyici de kullanilabilir.
    pause
    exit /b 1
)

echo.
echo Program kapandi.
pause

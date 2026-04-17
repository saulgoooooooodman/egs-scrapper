@echo off
chcp 65001 >nul
title EGS Scrapper Saglik Kontrolu

echo ==========================================
echo   EGS SCRAPPER SAGLIK KONTROLU BASLIYOR
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "health_check.py" (
    echo HATA: health_check.py bulunamadi.
    pause
    exit /b 1
)

echo [1/4] Python surumu kontrol ediliyor...
python --version
if errorlevel 1 (
    echo HATA: Python calismiyor veya PATH icinde degil.
    pause
    exit /b 1
)

echo.
echo [2/4] health_check.py calistiriliyor...
python health_check.py
set CHECK_RESULT=%ERRORLEVEL%

echo.
echo [3/4] Rapor dosyasi kontrol ediliyor...
if exist "health_check_report.txt" (
    echo Rapor olusturuldu:
    echo "%cd%\health_check_report.txt"
) else (
    echo UYARI: health_check_report.txt bulunamadi.
)

echo.
echo [4/4] Sonuc...
if "%CHECK_RESULT%"=="0" (
    echo ==========================================
    echo   SAGLIK KONTROLU BASARIYLA TAMAMLANDI
    echo ==========================================
) else (
    echo ==========================================
    echo   SAGLIK KONTROLUNDE HATALAR VAR
    echo ==========================================
)

echo.
pause
exit /b %CHECK_RESULT%
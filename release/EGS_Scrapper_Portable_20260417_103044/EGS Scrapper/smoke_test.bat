@echo off
chcp 65001 >nul
title EGS Scrapper Smoke Test

echo ==========================================
echo      EGS SCRAPPER SMOKE TEST BASLIYOR
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "smoke_test.py" (
    echo HATA: smoke_test.py bulunamadi.
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
echo [2/4] smoke_test.py calistiriliyor...
python smoke_test.py
set CHECK_RESULT=%ERRORLEVEL%

echo.
echo [3/4] Rapor dosyasi kontrol ediliyor...
if exist "smoke_test_report.txt" (
    echo Rapor olusturuldu:
    echo "%cd%\smoke_test_report.txt"
) else (
    echo UYARI: smoke_test_report.txt bulunamadi.
)

echo.
echo [4/4] Sonuc...
if "%CHECK_RESULT%"=="0" (
    echo ==========================================
    echo   SMOKE TEST BASARIYLA TAMAMLANDI
    echo ==========================================
) else (
    echo ==========================================
    echo   SMOKE TEST ICIN HATALAR VAR
    echo ==========================================
)

echo.
pause
exit /b %CHECK_RESULT%

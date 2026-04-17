@echo off
chcp 65001 >nul
title Import Duzeltici

echo ==========================================
echo   IMPORT YOLLARI DUZELTILIYOR
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "fix_imports.py" (
    echo HATA: fix_imports.py bulunamadi
    pause
    exit /b 1
)

python fix_imports.py

echo.
echo Islemler tamamlandi.
echo Her dosya icin .bak yedek olusturuldu.
echo.
pause
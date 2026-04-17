@echo off
chcp 65001 >nul
title EGS Scrapper - Proje Yedekleme

echo ==========================================
echo         EGS SCRAPPER YEDEKLEME
echo ==========================================
echo.

cd /d "%~dp0"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i

if not exist "backups" mkdir "backups"

set ZIPFILE=backups\EGS_Scrapper_Backup_%TS%.zip

powershell -NoProfile -Command ^
"Compress-Archive -Path * -DestinationPath '%ZIPFILE%' -Force"

if errorlevel 1 (
    echo Yedekleme basarisiz oldu.
    pause
    exit /b 1
)

echo Yedekleme tamamlandi:
echo %ZIPFILE%
echo.
pause
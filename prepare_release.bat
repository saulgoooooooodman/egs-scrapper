@echo off
chcp 65001 >nul
title EGS Scrapper - Release Hazirlama

echo ==========================================
echo       EGS SCRAPPER RELEASE HAZIRLAMA
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "dist\EGS Scrapper" (
    echo Once build_exe.bat calistirilmalidir.
    pause
    exit /b 1
)

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i

set "PORTABLE_DIR=release\EGS_Scrapper_Portable_%TS%"
set "UPDATE_DIR=release\EGS_Scrapper_Update_%TS%"
set "SOURCE_BACKUP=backups\EGS_Scrapper_PreRelease_%TS%.zip"
set "UPDATE_PAYLOAD=%UPDATE_DIR%\EGS Scrapper Update\payload"

echo [0/6] Surum oncesi kaynak yedegi aliniyor...
if not exist "backups" mkdir "backups"
powershell -NoProfile -Command ^
"$items = Get-ChildItem -Force ^| Where-Object { $_.Name -notin @('.git', 'backups', 'build', 'dist', 'release', '.venv', 'venv', 'env', '__pycache__') }; if (-not $items) { throw 'Yedeklenecek dosya bulunamadi.' }; Compress-Archive -Path $items.FullName -DestinationPath '%SOURCE_BACKUP%' -Force"
if errorlevel 1 (
    echo Kaynak yedegi alinamadi.
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [1/6] Release klasorleri olusturuluyor...
if not exist "release" mkdir "release"
mkdir "%PORTABLE_DIR%\EGS Scrapper"
mkdir "%UPDATE_PAYLOAD%"
echo Tamam.
echo.

echo [2/6] Tam portable paket hazirlaniyor...
xcopy /E /I /Y "dist\EGS Scrapper" "%PORTABLE_DIR%\EGS Scrapper" >nul
if exist "Start_EGS_Scrapper.bat" copy /Y "Start_EGS_Scrapper.bat" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "install_update.bat" copy /Y "install_update.bat" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "apply_update.bat" copy /Y "apply_update.bat" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "apply_update_gui.ps1" copy /Y "apply_update_gui.ps1" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "saglik_kontrolu.bat" copy /Y "saglik_kontrolu.bat" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "smoke_test.bat" copy /Y "smoke_test.bat" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "health_check.py" copy /Y "health_check.py" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "smoke_test.py" copy /Y "smoke_test.py" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "help_content.md" copy /Y "help_content.md" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "MINI_SURUM_REHBERI.md" copy /Y "MINI_SURUM_REHBERI.md" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "README.md" copy /Y "README.md" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "channel_rules.json" copy /Y "channel_rules.json" "%PORTABLE_DIR%\EGS Scrapper\" >nul
if exist "channel_logos" xcopy /E /I /Y "channel_logos" "%PORTABLE_DIR%\EGS Scrapper\channel_logos" >nul
echo Tamam.
echo.

echo [3/6] Update paketi hazirlaniyor...
xcopy /E /I /Y "dist\EGS Scrapper" "%UPDATE_PAYLOAD%" >nul
if exist "%UPDATE_PAYLOAD%\databases" rmdir /s /q "%UPDATE_PAYLOAD%\databases"
if exist "%UPDATE_PAYLOAD%\logs" rmdir /s /q "%UPDATE_PAYLOAD%\logs"
if exist "%UPDATE_PAYLOAD%\error_reports" rmdir /s /q "%UPDATE_PAYLOAD%\error_reports"
if exist "%UPDATE_PAYLOAD%\channel_dictionaries" rmdir /s /q "%UPDATE_PAYLOAD%\channel_dictionaries"
if exist "%UPDATE_PAYLOAD%\settings.json" del /q "%UPDATE_PAYLOAD%\settings.json"
if exist "%UPDATE_PAYLOAD%\common_dictionary.json" del /q "%UPDATE_PAYLOAD%\common_dictionary.json"
if exist "apply_update.bat" copy /Y "apply_update.bat" "%UPDATE_DIR%\EGS Scrapper Update\" >nul
if exist "apply_update_gui.ps1" copy /Y "apply_update_gui.ps1" "%UPDATE_DIR%\EGS Scrapper Update\" >nul
if exist "README.md" copy /Y "README.md" "%UPDATE_DIR%\EGS Scrapper Update\" >nul
if exist "help_content.md" copy /Y "help_content.md" "%UPDATE_DIR%\EGS Scrapper Update\" >nul
if exist "MINI_SURUM_REHBERI.md" copy /Y "MINI_SURUM_REHBERI.md" "%UPDATE_DIR%\EGS Scrapper Update\" >nul
echo Tamam.
echo.

echo [4/6] Guncelleme paketi kullanici verisini etkilemeyecek sekilde ayrildi.
echo Hedefte korunacak alanlar: settings, veritabanlari, loglar, hata raporlari, kanal sozlukleri.
echo.

echo [5/6] Kaynak yedegi:
echo %SOURCE_BACKUP%
echo.

echo [6/6] Release hazir.
echo.
echo Portable klasor:
echo %PORTABLE_DIR%\EGS Scrapper
echo.
echo Update klasoru:
echo %UPDATE_DIR%\EGS Scrapper Update
echo.
pause

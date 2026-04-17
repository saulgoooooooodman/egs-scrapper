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

set RELEASE_DIR=release\EGS_Scrapper_Portable_%TS%

echo [1/4] Release klasoru olusturuluyor...
if not exist "release" mkdir "release"
mkdir "%RELEASE_DIR%"
echo Tamam.
echo.

echo [2/4] Build dosyalari kopyalaniyor...
xcopy /E /I /Y "dist\EGS Scrapper" "%RELEASE_DIR%\EGS Scrapper" >nul
echo Tamam.
echo.

echo [3/4] Ek belgeler ve araclar ekleniyor...
if exist "install_update.bat" copy /Y "install_update.bat" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "Start_EGS_Scrapper.bat" copy /Y "Start_EGS_Scrapper.bat" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "saglik_kontrolu.bat" copy /Y "saglik_kontrolu.bat" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "smoke_test.bat" copy /Y "smoke_test.bat" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "health_check.py" copy /Y "health_check.py" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "smoke_test.py" copy /Y "smoke_test.py" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "help_content.md" copy /Y "help_content.md" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "channel_rules.json" copy /Y "channel_rules.json" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "common_dictionary.json" copy /Y "common_dictionary.json" "%RELEASE_DIR%\EGS Scrapper\" >nul
if exist "channel_logos" xcopy /E /I /Y "channel_logos" "%RELEASE_DIR%\EGS Scrapper\channel_logos" >nul
if exist "channel_dictionaries" xcopy /E /I /Y "channel_dictionaries" "%RELEASE_DIR%\EGS Scrapper\channel_dictionaries" >nul
echo Tamam.
echo.

echo [4/4] Release hazir.
echo.
echo Klasor:
echo %RELEASE_DIR%\EGS Scrapper
echo.
pause

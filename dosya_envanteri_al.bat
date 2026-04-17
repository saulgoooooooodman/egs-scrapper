@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title EGS Scrapper - Dosya Envanteri

cd /d "%~dp0"

set "OUT=%cd%\dosya_envanteri.txt"
set "TMPROOT=%temp%\egs_root_files_%random%.txt"
set "TMPNAMES=%temp%\egs_names_%random%.txt"

if exist "%OUT%" del /f /q "%OUT%" >nul 2>&1
if exist "%TMPROOT%" del /f /q "%TMPROOT%" >nul 2>&1
if exist "%TMPNAMES%" del /f /q "%TMPNAMES%" >nul 2>&1

echo EGS Scrapper Dosya Envanteri > "%OUT%"
echo Tarih: %date% %time%>> "%OUT%"
echo Klasor: %cd%>> "%OUT%"
echo.>> "%OUT%"

echo =========================================>> "%OUT%"
echo KOK KLASOR DOSYALARI>> "%OUT%"
echo =========================================>> "%OUT%"
for %%F in (*) do echo %%F>> "%OUT%"
echo.>> "%OUT%"

echo =========================================>> "%OUT%"
echo KLASOR YAPISI>> "%OUT%"
echo =========================================>> "%OUT%"
tree /f /a >> "%OUT%"
echo.>> "%OUT%"

echo =========================================>> "%OUT%"
echo SADECE PY DOSYALARI (TAM YOL)>> "%OUT%"
echo =========================================>> "%OUT%"
for /r %%F in (*.py) do echo %%F>> "%OUT%"
echo.>> "%OUT%"

echo =========================================>> "%OUT%"
echo KOKTE OLUP ALT KLASORLERDE DE AYNI ISIMLE BULUNAN DOSYALAR>> "%OUT%"
echo =========================================>> "%OUT%"

for %%F in (*) do echo %%~nxF>> "%TMPROOT%"

set "HAS_DUP=0"
for /f "usebackq delims=" %%R in ("%TMPROOT%") do (
    set /a COUNT=0
    for /r %%F in (*) do (
        if /I "%%~nxF"=="%%R" set /a COUNT+=1
    )
    if !COUNT! GTR 1 (
        echo %%R>> "%OUT%"
        set "HAS_DUP=1"
    )
)

if "!HAS_DUP!"=="0" echo Cakisan dosya bulunamadi.>> "%OUT%"
echo.>> "%OUT%"

echo =========================================>> "%OUT%"
echo KOK KLASORDEKI MUHTEMEL ARTIK DOSYALAR (PY / BAK / PYC)>> "%OUT%"
echo =========================================>> "%OUT%"
for %%F in (*.py *.bak *.pyc) do echo %%F>> "%OUT%"
echo.>> "%OUT%"

del /f /q "%TMPROOT%" >nul 2>&1
del /f /q "%TMPNAMES%" >nul 2>&1

echo Envanter olusturuldu:
echo %OUT%
echo.
pause
endlocal
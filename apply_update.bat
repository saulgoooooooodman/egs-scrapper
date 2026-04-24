@echo off
chcp 65001 >nul
title EGS Scrapper - Guncelleme
setlocal EnableExtensions

cd /d "%~dp0"

if exist "%~dp0apply_update_gui.ps1" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0apply_update_gui.ps1"
    exit /b %errorlevel%
)

echo Guncelleme arayuzu bulunamadi.
echo apply_update_gui.ps1 eksik gorunuyor.
pause


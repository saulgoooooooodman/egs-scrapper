@echo off
chcp 65001 >nul
title EGS Scrapper - Build Temizleme

echo ==========================================
echo         EGS SCRAPPER BUILD TEMIZLE
echo ==========================================
echo.

cd /d "%~dp0"

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "app.spec" del /f /q "app.spec"

echo Temizlik tamamlandi.
echo.
pause
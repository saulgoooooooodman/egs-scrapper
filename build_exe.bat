@echo off
chcp 65001 >nul
title EGS Scrapper - EXE Derleme

echo ==========================================
echo          EGS SCRAPPER EXE DERLEME
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/8] Python kontrol ediliyor...
python --version >nul 2>nul
if errorlevel 1 (
    echo Python bulunamadi.
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [2/8] Pip kontrol ediliyor...
python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo Pip bulunamadi.
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [3/8] Gerekli kutuphaneler kuruluyor/kontrol ediliyor...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Kutuphane kurulumu basarisiz.
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [4/8] PyInstaller modulu kontrol ediliyor...
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo PyInstaller import edilemedi.
    echo Elle kurmayi dene:
    echo python -m pip install pyinstaller
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [5/8] Eski build klasorleri temizleniyor...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo Tamam.
echo.

echo [6/8] logo.ico kontrol ediliyor...
if not exist "logo.ico" (
    echo UYARI: logo.ico bulunamadi.
    echo EXE iconsuz derlenecek.
) else (
    echo logo.ico bulundu.
)
echo.

echo [7/8] PyInstaller spec ile derleniyor...
python -m PyInstaller --noconfirm --clean "EGS_Scrapper.spec"
if errorlevel 1 (
    echo EXE derleme basarisiz oldu.
    pause
    exit /b 1
)
echo Tamam.
echo.

echo [8/8] Gerekli klasorler hazirlaniyor...
if not exist "dist\EGS Scrapper\databases" mkdir "dist\EGS Scrapper\databases"
if not exist "dist\EGS Scrapper\logs" mkdir "dist\EGS Scrapper\logs"
if not exist "dist\EGS Scrapper\error_reports" mkdir "dist\EGS Scrapper\error_reports"
echo Tamam.
echo.

echo Derleme tamamlandi.
echo.
echo Cikti klasoru:
echo dist\EGS Scrapper
echo.
pause
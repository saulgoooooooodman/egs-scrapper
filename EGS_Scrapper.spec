# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

base_dir = Path.cwd()

datas = []

for filename in [
    "logo.svg",
    "logo.png",
    "logo.ico",
    "help_content.md",
    "channel_rules.json",
    "common_dictionary.json",
]:
    file_path = base_dir / filename
    if file_path.exists():
        datas.append((str(file_path), "."))

for dirname in ["channel_logos", "channel_dictionaries"]:
    dir_path = base_dir / dirname
    if dir_path.exists():
        datas.append((str(dir_path), dirname))

datas += collect_data_files("wordfreq")

a = Analysis(
    ["app.py"],
    pathex=[str(base_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=["rapidfuzz"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EGS Scrapper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(base_dir / "logo.ico") if (base_dir / "logo.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="EGS Scrapper",
)

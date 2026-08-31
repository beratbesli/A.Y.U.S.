# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_dir = Path(SPECPATH)


a = Analysis(
    [str(project_dir / "A.Y.U.S..py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[(str(project_dir / "depremfoto.png"), ".")],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name="A.Y.U.S",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

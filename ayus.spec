import sys
from pathlib import Path


project_dir = Path(SPECPATH)

datas = [(str(project_dir / "depremfoto.png"), ".")]
icon_path = project_dir / "assets" / "ayus.png"
if icon_path.is_file():
    datas.append((str(icon_path), "assets"))

binaries = []
if sys.platform.startswith("linux"):
    base_lib = Path(sys.base_prefix) / "lib"
    for lib_file in base_lib.glob("libtcl*.so*"):
        binaries.append((str(lib_file), "."))
    for lib_file in base_lib.glob("libtk*.so*"):
        binaries.append((str(lib_file), "."))


a = Analysis(
    [str(project_dir / "A.Y.U.S..py")],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
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

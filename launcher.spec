# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for OmniVoice Launcher.

Builds a small (~7 MB) launcher exe that:
  1. Creates a Python venv on first run (omnivoice_env/)
  2. Installs torch, transformers, omnivoice, etc.
  3. Launches the Gradio demo at http://localhost:7860

Heavy ML libraries are NOT bundled — installed at runtime into omnivoice_env/.
"""

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['argparse', 'subprocess', 'os', 'sys'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchaudio', 'transformers', 'gradio',
        'numpy', 'scipy', 'sklearn', 'matplotlib',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OmniVoice',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

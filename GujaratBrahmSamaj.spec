# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None
project_root = os.path.abspath(SPECPATH)

datas = [
    (os.path.join(project_root, 'assets', 'fonts'), os.path.join('assets', 'fonts')),
    (os.path.join(project_root, 'assets', 'images'), os.path.join('assets', 'images')),
    (os.path.join(project_root, 'assets', 'icons'), os.path.join('assets', 'icons')),
]

hiddenimports = [
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.sql.default_comparator',
    'reportlab',
    'reportlab.platypus',
    'reportlab.lib',
    'reportlab.pdfgen',
    'reportlab.graphics',
    'openpyxl',
    'PIL',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
]

a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', '_pytest', 'tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GujaratBrahmSamaj',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'assets', 'icons', 'app_icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GujaratBrahmSamaj',
)

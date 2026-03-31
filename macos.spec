# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/helvox/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('src/helvox/resources', 'helvox/resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Helvox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='Helvox.app',
    icon=None,
    bundle_identifier='io.noxenum.helvox',
    info_plist={
        'NSMicrophoneUsageDescription': 'Helvox needs microphone access to record speech samples.',
    },
)

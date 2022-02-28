# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

folders = [
('.\\img', '.\\img'),
('.\\functions', '.\\functions'),
('.\\logs', '.\\logs')
]

a = Analysis(['Monitor.py'],
             pathex=['%USERPROFILE%\\PycharmProjects\\Monitor'],
             binaries=[],
             datas=folders,
             hiddenimports=['pywintypes'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Monitor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='.\\img\image.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Monitor')

# -*- mode: python ; coding: utf-8 -*-

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils
import os
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/Users/kevinw/projects/draw-python'],
             binaries=[],
             datas=[],
             hiddenimports=['PySide2'],
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
          name='Draw',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Draw')
app = BUNDLE(coll,
             name='Draw.app',
             icon=None,
             bundle_identifier=None)

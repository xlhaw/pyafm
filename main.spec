# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew#, gstreamer
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, get_deps_all, hookspath, runtime_hooks
block_cipher = None
import sys
sys.setrecursionlimit(5000)

a = Analysis(['main.py'],
             pathex=['E:\\zwPython\\py37\\notebooks\\pyafm'],
             datas=[],
			 hookspath=hookspath(),
             runtime_hooks=runtime_hooks(),
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False,
			 **get_deps_minimal(),
			 #**get_deps_all(),
			 )
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
			   *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins )],#+ gstreamer.dep_bins
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')

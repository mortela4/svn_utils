# -*- mode: python -*-

block_cipher = None


a = Analysis(['svn_rev_update\\svn_rev_update.py'],
             pathex=['C:\\Users\\larsenm\\Documents\\div\\pro\\svn_utils'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='svn_rev_update',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

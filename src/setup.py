from cx_Freeze import setup, Executable
from VERSION import version
import sys
import os
from glob import glob

# Dependencies are automatically detected, but it might need
# fine tuning.
shortcut_table = [
    ("PeachyPrinterTools",                  # Shortcut
     "DesktopFolder",                       # Directory_
     "Peachy Printer Tools",                # Name
     "TARGETDIR",                           # Component_
     "[TARGETDIR]PeachyPrinterTools.exe",   # Target
     None,                                  # Arguments
     None,                                  # Description
     None,                                  # Hotkey
     None,                                  # Icon
     None,                                  # IconIndex
     None,                                  # ShowCmd
     'TARGETDIR'                            # WkDir
     )
    ]

buildOptions = { 
        'packages' : ['domain','infrastructure','api','ui'], 
        'excludes' : [],
        'icon' : os.path.join('resources', 'peachy.ico'),
        }

bdist_dmg_options = { }

bdist_mac_options = { 'iconfile': os.path.join('resources', 'peachy.icns') } 
#Note to james use img2icns and iconutil first to iconset then to icns

bdist_msi_options = { 'data': { 'Shortcut' : shortcut_table } }


base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('peachyprintertools.py', base=base, targetName = 'PeachyPrinterTools.exe')
]

setup(
      name='PeachyPrinterTools',
      version = version,
      description = 'Tool Set for calibrating the Peachy Printer and printing models',
      options =  { 'build_exe' : buildOptions,  "bdist_msi": bdist_msi_options, 'bdist_dmg' : bdist_dmg_options, 'bdist_mac' : bdist_mac_options },
      data_files = [('resources',glob('resources/*'))],
      packages=['domain','infrastructure','api','ui'], 
      py_modules=['VERSION','peachyprintertools'],
      executables = executables
      )

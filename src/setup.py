from cx_Freeze import setup, Executable
from VERSION import version
import sys

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
    packages : ['domain','infrastructure'], 
    excludes : [],
    "Shortcut": shortcut_table
    }

base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('peachyprintertools.py', base=base, targetName = 'PeachyPrinterTools.exe')
]

setup(name='Peachy Printer Tools',
      version = version,
      description = 'Tool Set for calibrating the Peachy Printer and printing models',
      options = { build_exe = buildOptions },
      executables = executables
      )

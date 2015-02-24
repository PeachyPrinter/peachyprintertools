from cx_Freeze import setup
from VERSION import version
import sys
import os

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

base = 'Win32GUI' if sys.platform == 'win32' else None

setup(
      name='PeachyPrinterToolsAPI',
      version=version,
      description='Tool Set for calibrating the Peachy Printer and printing models',
      options={},
      data_files=[],
      packages=['domain', 'infrastructure', 'api'],
      py_modules=['VERSION'],
      )

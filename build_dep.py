import os
import sys
import shutil

python_64 = sys.maxsize > 2**32

source_dir = os.path.dirname(__file__)

if os.name == 'nt':
    if python_64:
        dep_path = os.path.join(source_dir, 'dependancies', 'win', 'amd64')
    else:
        dep_path = os.path.join(source_dir, 'dependancies', 'win', 'x86')

    libusb10_dll = os.path.join(dep_path, 'libusb-1.0.dll')
    shutil.copy(libusb10_dll, os.path.join(source_dir, 'src', 'peachyprinter'))

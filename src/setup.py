from setuptools import setup, find_packages
from setuptools.command.install import install as _Install
from VERSION import version
import os
import glob

# data_files = [('peachyprinter/resources/dll', ["peachyprinter/dll/libusb-1.0.dll"])]

setup(
    name='PeachyPrinterToolsAPI',
    version=version,
    description='Tool Set for calibrating the Peachy Printer and printing models',
    options={},
    url="http://www.peachyprinter.com",
    author="Peachy Printer",
    author_email="software+peachyprintertools@peachyprinter.com",
    package_data={'': ['*.dll', 'peachyprinter/dependancies/win/amd64/*'],
                  '': ['*.dll', 'peachyprinter/dependancies/win/x86/*'],
                  '': ['*.dylib', 'peachyprinter/dependancies/mac/amd64/*'],
                  '': ['*.so', 'peachyprinter/dependancies/linux/amd64/*'],
                  '': ['*.bin', 'peachyprinter/dependancies/firmware/*']
                  },
    dependency_links=['https://github.com/PeachyPrinter/peachy-firmware-flash/releases/download/0.0.1.49/PeachyPrinterFirmwareAPI-0.0.1.49.tar.gz'],
    install_requires=[
      'protobuf>=2.6.1',
      'pyserial>=2.7',
      'numpy>=1.9.2',
      'libusb1>=1.3.1',
      'PeachyPrinterFirmwareAPI>=0.0.1.49'
    ],
    packages=find_packages(),
    py_modules=['VERSION'],
    include_package_data=True
      )

class install(_Install):
    def run(self):
        super(install, self).run(self)
        print "BADA-BADA-KABONG"
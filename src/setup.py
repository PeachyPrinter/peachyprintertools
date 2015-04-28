from setuptools import setup, find_packages
from setuptools.command.install import install as _Install
from VERSION import version
import os

data_files = [('resources/dll', ["resources/dll/libusb-1.0.dll"])]

setup(
    name='PeachyPrinterToolsAPI',
    version=version,
    description='Tool Set for calibrating the Peachy Printer and printing models',
    options={},
    url="http://www.peachyprinter.com",
    author="Peachy Printer",
    author_email="software+peachyprintertools@peachyprinter.com",
    data_files=data_files,
    zip_safe=False,
    install_requires=['protobuf>=2.6.1', 'pyserial>=2.7', 'numpy>=1.8.2', 'libusb1>=1.3.1'],
    packages=find_packages(),
    py_modules=['VERSION'],
    include_package_data=True
      )

class install(_Install):
    def run(self):
        super(install, self).run(self)
        print "BADA-BADA-KABONG"
from setuptools import setup, find_packages
from VERSION import version

setup(
      name='PeachyPrinterToolsAPI',
      version=version,
      description='Tool Set for calibrating the Peachy Printer and printing models',
      options={},
      url="http://www.peachyprinter.com",
      author="Peachy Printer",
      author_email="software+peachyprintertools@peachyprinter.com",
      data_files=[],
      install_requires=['protobuf>=2.6.1', 'pyserial>=2.7', 'numpy>=1.8.2'],
      packages=find_packages(),
      py_modules=['VERSION'],
      include_package_data=True
      )

from setuptools import setup
from VERSION import version

setup(
      name='PeachyPrinterToolsAPI',
      version=version,
      description='Tool Set for calibrating the Peachy Printer and printing models',
      options={},
      data_files=[],
      install_requires=['protobuf==2.6.1', 'pyserial==2.7'],
      packages=['domain', 'infrastructure', 'api'],
      py_modules=['VERSION'],
      )

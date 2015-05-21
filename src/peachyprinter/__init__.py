import os
import sys
import logging

logger = logging.getLogger('peachy')

if os.name == 'nt':
    import ctypes
    import pkg_resources
    from pkg_resources import DistributionNotFound

    python_64 = sys.maxsize > 2**32

    try:
        dist = pkg_resources.get_distribution('PeachyPrinterToolsAPI')
        if python_64:
            dep_path = os.path.join(dist,'peachyprinter' ,'dependancies', 'win', 'amd64')
        else:
            dep_path = os.path.join(dist,'peachyprinter' ,'dependancies', 'win', 'x86')
        dll_path = os.path.join(dep_path, 'libusb-1.0.dll')

    except Exception:
        current_path = os.path.dirname(__file__)
        if python_64:
            dep_path = os.path.join(current_path, '..','peachyprinter' ,'dependancies', 'win', 'amd64')
        else:
            dep_path = os.path.join(current_path, '..','peachyprinter' ,'dependancies', 'win', 'x86')

        dll_path = os.path.join(dep_path, 'libusb-1.0.dll')

    logging.info("Attempting Loading usb dll from: %s" % dll_path)
    try:
        ctypes.cdll.LoadLibrary(dll_path)
    except Exception as ex:
        logging.error("Failed Loading usb dll from: %s" % dll_path)
        raise

from peachyprinter.api.peachy_printer_api import PrinterAPI
from peachyprinter.infrastructure.communicator import MissingPrinterException


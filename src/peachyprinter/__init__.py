import os
if os.name == 'nt':
    import ctypes
    import pkg_resources
    from pkg_resources import DistributionNotFound

    try:
        dist = pkg_resources.get_distribution('PeachyPrinterToolsAPI')
        dll_path = os.path.join(dist.location, 'peachyprinter', 'libusb-1.0.dll')
    except DistributionNotFound:
        dll_path = os.path.join(os.path.dirname(__file__), 'libusb-1.0.dll')

    print("Attempting Loading usb dll from: %s" % dll_path)
    try:
        ctypes.cdll.LoadLibrary(dll_path)
    except:
        print("Failed Loading usb dll from: %s" % dll_path)

from peachyprinter.api.peachy_printer_api import PrinterAPI
from peachyprinter.infrastructure.communicator import MissingPrinterException

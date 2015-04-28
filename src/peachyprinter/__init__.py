import os
if os.name == 'nt':
	import ctypes
	import pkg_resources
	dist = pkg_resources.get_distribution('PeachyPrinterToolsAPI')
	dll_path = os.path.join(dist.location, 'resources','dll','libusb-1.0.dll')
	ctypes.cdll.LoadLibrary(dll_path)

from peachyprinter.api.peachy_printer_api import PrinterAPI

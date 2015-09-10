# -*- mode: python; basic-offset: 4 -*-
import os
import sys
import logging

logger = logging.getLogger('peachy')

from peachyprinter.api.peachy_printer_api import PrinterAPI
from peachyprinter.infrastructure.communicator import MissingPrinterException

try:
    from VERSION import version
except:
    version = "DEV"

try:
    from infrastructure.peachyusb import version as lib_version
except:
    lib_version = "Unknown"
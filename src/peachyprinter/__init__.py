# -*- mode: python; basic-offset: 4 -*-
import os
import sys
import logging
import affinity

if sys.platform != 'darwin':
    affinity.set_process_affinity_mask(0, 0x00000001)
    
logger = logging.getLogger('peachy')
    
from peachyprinter.api.peachy_printer_api import PrinterAPI
from peachyprinter.infrastructure.communicator import MissingPrinterException


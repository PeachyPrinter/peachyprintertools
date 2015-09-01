#!/usr/bin/env python

# Script to demonstrate the use of the peachyprintertools API to
# display a test pattern on the Peachy Printer

import peachyprinter
import logging
import time

def setup_logging():
    logger = logging.getLogger('peachy')

    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = "INFO"

    logger.propagate = False
    logFormatter = logging.Formatter(logging_format)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging_level)
    return logger

logger = setup_logging()

logger.info("Starting up test pattern")

api = peachyprinter.PrinterAPI()
api.load_printer()

print "Loaded %s " % (api.current_printer(),)
calibration_api = api.get_calibration_api()

calibration_api.show_point([0.5, 0.5, 0.0])
try:
    time.sleep(60)
except KeyboardInterrupt:
    pass
calibration_api.close()
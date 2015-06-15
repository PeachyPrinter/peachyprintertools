#!/usr/bin/env python

# Script to demonstrate the use of the peachyprintertools API to
# display a test pattern on the Peachy Printer

import peachyprinter

api = peachyprinter.PrinterAPI()
api.load_printer()

print "Loaded %s " % (api.current_printer(),)
calibration_api = api.get_calibration_api()
calibration_api.show_point([0.5, 0.5, 0.0])

calibration_api.close()
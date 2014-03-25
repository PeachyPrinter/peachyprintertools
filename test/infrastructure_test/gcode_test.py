import unittest
import StringIO
import os
import sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.gcode import GCodeReader

class GCodeReaderTests(unittest.TestCase):
    
    def test_check_ignores_comments(self):
        test_gcode = StringIO.StringIO(";Comment\nG1 X0.00 Y0.00 E0\n")

        gcode_reader = GCodeReader()
        self.assertEquals([], gcode_reader.check(test_gcode))

    def test_check_should_report_error_on_non_gcode(self):
        line = "Fake Gcode"
        test_gcode = StringIO.StringIO("%s\n" % line)

        gcode_reader = GCodeReader()
        self.assertEquals(["Unreconized Command 1: %s" % line ] , gcode_reader.check(test_gcode))

if __name__ == '__main__':
    unittest.main()
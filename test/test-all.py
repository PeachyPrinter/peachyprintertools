import unittest
import os
import ctypes
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', ))

if os.name == 'nt':
	dll_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'peachyprinter', 'libusb-1.0.dll')
	ctypes.cdll.LoadLibrary(dll_path)


loader = unittest.TestLoader()
suite = loader.discover(os.path.dirname(__file__), pattern='*test.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

problems = len(result.errors) + len(result.failures)
print("\nProblems: %s\n" % problems)
exit(problems)

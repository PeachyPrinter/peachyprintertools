import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', ))

if os.name == 'nt':
    import ctypes

    python_64 = sys.maxsize > 2**32

    current_path = os.path.dirname(__file__)
    if python_64:
        dep_path = os.path.join(current_path, '..', 'src','peachyprinter', 'dependancies', 'win', 'amd64')
    else:
        dep_path = os.path.join(current_path, '..', 'src','peachyprinter', 'dependancies', 'win', 'x86')

    dll_path = os.path.join(dep_path, 'libusb-1.0.dll')

    if not os.path.isfile(dll_path):
        print('libusb missing')
    print('Loading usb dll: %s' % dll_path)
    try:
        ctypes.cdll.LoadLibrary(dll_path)
    except Exception as ex:
        print("Loading library fails: ")
        print(ex)
        exit(324)


loader = unittest.TestLoader()
suite = loader.discover(os.path.dirname(__file__), pattern='*test.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

problems = len(result.errors) + len(result.failures)
print("\nProblems: %s\n" % problems)
exit(problems)

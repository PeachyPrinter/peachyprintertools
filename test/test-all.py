import unittest
import os
import sys
import pyaudio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', ))


loader = unittest.TestLoader()
suite = loader.discover(os.path.dirname(__file__), pattern='*test.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

problems = len(result.errors) + len(result.failures)
print("\nProblems: %s\n" % problems)
exit(problems)

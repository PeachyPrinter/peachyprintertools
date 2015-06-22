import ctypes
import pkg_resources
from pkg_resources import DistributionNotFound
import os
import sys
import logging

def ensure_windows_dependancies():
    try:
        from ctypes import cdll
        cdll.msvcp120
        print "success"
    except WindowsError:
        logging.error("Could not find MS c++ redist-brutal, will prompt for install")
        import webbrowser
        import win32api

        win32api.MessageBox(0, 'Visual C++ Redistributable for Visual Studio 2012 is required to run. Your browser should open on microsofts download page', 'One more thing!')

        url = "https://www.microsoft.com/en-ca/download/details.aspx?id=30679"
        new = 2 # new tab
        webbrowser.open(url, new=new)
        raise EnvironmentError("Could not find MS c++ redist-brutal, will prompt for install")
    return True

def load_library(name):
    suffix = ''
    python_64 = sys.maxsize > 2**32
    if sys.platform == 'linux2':
        suffix = '.so'
        dependency_platform = 'linux'
    if sys.platform == 'darwin':
        suffix = '.dylib'
        dependency_platform = 'mac'
    if os.name == 'nt':
        ensure_windows_dependancies()
        suffix = '.dll'
        dependency_platform = 'win'

    if os.environ.get('PEACHY_API_DLL_PATH'):
        dll_path = os.environ.get('PEACHY_API_DLL_PATH')
        logging.info("Loading usb dll via PEACHY_API_DLL_PATH")
    else:
        try:
            dist = pkg_resources.get_distribution('PeachyPrinterToolsAPI')
            if python_64:
                dll_path = os.path.join(dist, 'peachyprinter', 'dependancies', dependency_platform, 'amd64')
            else:
                dll_path = os.path.join(dist,'peachyprinter', 'dependancies', dependency_platform, 'x86')
            logging.info("Loading usb dll via package resources")
        except Exception:
            current_path = os.path.dirname(__file__)
            if python_64:
                dll_path = os.path.join(current_path, '..', 'peachyprinter', 'dependancies', dependency_platform, 'amd64')
            else:
                dll_path = os.path.join(current_path, '..', 'peachyprinter', 'dependancies', dependency_platform, 'x86')
            logging.info("Loading usb dll via relitive path")
    
    dll_name = "%s%s" % (name, suffix)
    try:
        return ctypes.cdll.LoadLibrary(dll_name)
    except Exception as ex:
        logging.info("Failed loading dll by name: %s" % (dll_name,))

    try:
        dll_path = os.path.join(dll_path, dll_name)
        return ctypes.cdll.LoadLibrary(dll_path)
    except Exception as ex:
        logging.error("Failed loading dll from: %s" % (dll_path,))
        raise

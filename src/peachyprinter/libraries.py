import ctypes
import pkg_resources
from pkg_resources import DistributionNotFound    
import os
import sys
import logging

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
        suffix = '.dll'
        dependency_platform = 'win'

    if os.environ.get('PEACHY_API_DLL_PATH'):
        dll_path = os.environ.get('PEACHY_API_DLL_PATH')
        logging.info("Loading usb dll via PEACHY_API_DLL_PATH")
    else:
        try:
            dist = pkg_resources.get_distribution('PeachyPrinterToolsAPI')
            if python_64:
                dll_path = os.path.join(dist,'peachyprinter' ,'dependancies', dependency_platform, 'amd64')
            else:
                dll_path = os.path.join(dist,'peachyprinter' ,'dependancies', dependency_platform, 'x86')
            logging.info("Loading usb dll via package resources")
        except Exception:
            current_path = os.path.dirname(__file__)
            if python_64:
                dll_path = os.path.join(current_path, '..','peachyprinter' ,'dependancies', dependency_platform, 'amd64')
            else:
                dll_path = os.path.join(current_path, '..','peachyprinter' ,'dependancies', dependency_platform, 'x86')
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

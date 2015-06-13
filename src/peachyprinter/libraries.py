import ctypes
import pkg_resources
from pkg_resources import DistributionNotFound    
import os
import logging

def load_library(name):
    suffix = ''
    if os.name == 'posix':
        suffix = '.so'
        dll_path = '.'
    if os.name == 'nt':
        suffix = '.dll'
        python_64 = sys.maxsize > 2**32
        if os.environ.get('PEACHY_API_DLL_PATH'):
            dep_path = os.environ.get('PEACHY_API_DLL_PATH')
            logging.info("Loading usb dll via PEACHY_API_DLL_PATH")
        else:
            try:
                dist = pkg_resources.get_distribution('PeachyPrinterToolsAPI')
                if python_64:
                    dep_path = os.path.join(dist,'peachyprinter' ,'dependancies', 'win', 'amd64')
                else:
                    dep_path = os.path.join(dist,'peachyprinter' ,'dependancies', 'win', 'x86')
                logging.info("Loading usb dll via package resources")
            except Exception:
                current_path = os.path.dirname(__file__)
                if python_64:
                    dep_path = os.path.join(current_path, '..','peachyprinter' ,'dependancies', 'win', 'amd64')
                else:
                    dep_path = os.path.join(current_path, '..','peachyprinter' ,'dependancies', 'win', 'x86')
                logging.info("Loading usb dll via relitive path")
        dll_path = os.path.join(dep_path)
    
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

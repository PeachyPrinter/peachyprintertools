from peachyprinter.libraries import load_library
import ctypes

class peachyusb_t(ctypes.Structure):
    pass

peachyusb_t_p = ctypes.POINTER(peachyusb_t)

peachyusb_read_callback = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_char), ctypes.c_uint)

def _load_library():
    dll = load_library("libPeachyUSB")
    dll.peachyusb_init.argtypes = [ctypes.c_uint]
    dll.peachyusb_init.restype = peachyusb_t_p
    
    dll.peachyusb_set_read_callback.argtypes = [peachyusb_t_p, peachyusb_read_callback]
    dll.peachyusb_set_read_callback.restype = None

    dll.peachyusb_write.argtypes = [peachyusb_t_p, ctypes.c_char_p, ctypes.c_uint]
    dll.peachyusb_write.restype = None

    dll.peachyusb_version.argtypes = []
    dll.peachyusb_version.restype = ctypes.c_char_p
    return dll

lib = _load_library()

lib_version = lib.peachyusb_version()

class PeachyUSBException(Exception):
    pass

class PeachyUSB(object):
    def __init__(self, capacity):
        self.context = lib.peachyusb_init(capacity)
        if not self.context:
            raise PeachyUSBException("No printer found")

    def __del__(self):
        lib.peachyusb_shutdown(self.context)
        self.context = None

    def write(self, buf):
        if not self.context:
            raise PeachyUSBException("No printer found")
        lib.peachyusb_write(self.context, buf, len(buf))
        
    def set_read_callback(self, func):
        if not self.context:
            raise PeachyUSBException("No printer found")
        self._read_callback = peachyusb_read_callback(func)
        lib.peachyusb_set_read_callback(self.context, self._read_callback)
        


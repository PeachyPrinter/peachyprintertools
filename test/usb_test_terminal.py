#!/usr/bin/python
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.infrastructure.messages import *

class UsbTestTerminal(object):
    def __init__(self,verbose=False):
        self._verbose=verbose

        self._drips=0
        self._serial=None
        self._swrev=None
        self._hwrev=None
        self._adcNum=0
        self._adcVal=0
        self._dataRate=None

        self._usb = UsbPacketCommunicator(10)
        self._usb.register_handler(IAmMessage, self.i_am_handler)
        self._usb.register_handler(DripRecordedMessage, self.drip_handler)
        self._usb.register_handler(ReturnAdcValMessage, self.adc_handler)
        self._usb.start()
        if verbose:
            print "Started usb terminal"
        time.sleep(0.1)

    def usb_close(self):
        self._usb.close()

    def set_drips(self,dripCount=0):
        self._usb.send(SetDripCountMessage(dripCount))

    def identify(self):
        self._usb.send(IdentifyMessage())

    def enter_bootloader(self):
        self._usb.send(EnterBootloaderMessage())

    def get_adc_val(self,adcNum):
        self._adcNum=adcNum
        self._usb.send(GetAdcValMessage(adcNum))
        if self._verbose:
            print('adcNum: {0}'.format(adcNum))

    def adc_handler(self,message):
        self._adcVal=message.adcVal
        if self._verbose:
            print('adcNum: {0} adcVal: {1}'.format(self._adcNum, self._adcVal))

    def drip_handler(self, message):
        self._drips=message.drips
        if self._verbose:
            print('Recieved drip: {0}'.format(message.drips))

    def i_am_handler(self, message):
        self._serial=message.sn
        self._swrev=message.swrev
        self._hwrev=message.hwrev
        self._dataRate=message.dataRate
        if self._verbose:
            print('Serial number: {0}'.format(message.sn))
            print('SW rev number: {0}'.format(message.swrev))
            print('HW rev number: {0}'.format(message.hwrev))
            print('Data Rate:     {0}'.format(message.dataRate))

if __name__ == '__main__':
    t = UsbTestTerminal(verbose=True); 
    t.identify()
    t.set_drips(0)
    #t.enter_bootloader()
    while(1):
        t.get_adc_val(0)
        time.sleep(1)
        t.get_adc_val(1)
        time.sleep(1)
        t.get_adc_val(2)
        time.sleep(1)
        t.get_adc_val(3)
        time.sleep(1)
        t.get_adc_val(4)
        time.sleep(1)
        t.get_adc_val(5)
        time.sleep(1)
        t.get_adc_val(6)
        time.sleep(1)
        t.get_adc_val(7)
        time.sleep(1)
        t.get_adc_val(8)
        time.sleep(1)





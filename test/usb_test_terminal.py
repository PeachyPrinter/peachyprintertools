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
        self._adcNum=[]
        self._adcVal=[]
        self._dataRate=None
        self._adcCals=[]

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

    #A non-ideal push/pop queue interface.
    #Doesn't account for mis-matching - May be worth clearing on each request?
    def pop_adc(self,timeout=0.1):
        start=time.time()
        timeout=start+timeout #in seconds
        while(time.time()<timeout): #wait for data being available or 
            if (len(self._adcVal) != 0):
                tmp=[self._adcNum[0],self._adcVal[0]]
                del self._adcNum[0]
                del self._adcVal[0]
                return tmp
            else:
                time.sleep(0.01)

    def clear_adc_queues(self):
        self._adcNum=[]
        self._adcVal=[]

    def get_adc_calibrations(self):
        if len(self._adcCals)!=3:
            [adcNum,adcVrefCal]=self.get_adc_val(0)
            [adcNum,adcTemp30]=self.get_adc_val(1)
            [adcNum,adcTemp110]=self.get_adc_val(2)
            self._adcCals=[adcVrefCal,adcTemp30,adcTemp110]

    def get_temperature(self):

        self.get_adc_calibrations()

        #Return actual Temperature in C
        #Formula taken from STM32F0 datasheet page 252
        adcVrefCal=self._adcCals[0]
        adcTemp30=self._adcCals[1]
        adcTemp110=self._adcCals[2]

        #Get the current Vref and Temperature each time
        [adcNum,adcTemperature]=self.get_adc_val(5)
        [adcNum,adcVref]=self.get_adc_val(6)

        #... what a mess...
        vrefCompensation = 1.0*adcVrefCal/adcVref
        temperature = adcTemperature*vrefCompensation-adcTemp30
        temperature = temperature*(110-30)/(adcTemp110-adcTemp30)
        temperature = temperature + 30

        if (self._verbose):
            print ('Temperatures Value={0} Celcius={1}'.format(adcTemperature,temperature))

        return temperature

    def get_supply_voltage(self):

        self.get_adc_calibrations()
        adcVrefCal=self._adcCals[0]
        [adcNum,adcVref]=self.get_adc_val(6)

        vrefCompensation = 1.0*adcVrefCal/adcVref
        
        #calibrated at 3.3V always
        supplyVoltage = 3.3*vrefCompensation

        if (self._verbose):
            print ('Voltage {0}, Value {1}'.format(supplyVoltage,adcVref))

        return supplyVoltage


    #ADC NUMBERS:
    #0 - Vref Calibration Factor
    #1 - 30C temperature calibration
    #2 - 110C temperature calibration
    #3 - ADC key (PA2)
    #4 - Pin (PA3)
    #5 - Temperature
    #6 - Vref (3.3V volts)
    def get_adc_val(self,adcNum):
        self._adcNum.append(adcNum)
        self._usb.send(GetAdcValMessage(adcNum))
        if self._verbose:
            print('adcNum: {0}'.format(adcNum))
        return self.pop_adc()

    def adc_handler(self,message):
        if (len(self._adcNum) > len(self._adcVal)):
            self._adcVal.append(message.adcVal)
            if self._verbose:
                print('adcNum: {0} adcVal: {1}'.format(self._adcNum[-1], self._adcVal[-1]))
        else:
            self.clear_adc_queues()

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
        t.get_temperature()
        t.get_supply_voltage()






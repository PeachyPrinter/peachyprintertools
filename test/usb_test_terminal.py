#!/usr/bin/python
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.infrastructure.messages import *

    #ADC NUMBERS:
    #0 - Vref Calibration Factor
    #1 - 30C temperature calibration
    #2 - 110C temperature calibration
    #3 - ADC key (PA2)
    #4 - Pin (PA3)
    #5 - Temperature
    #6 - Vref (3.3V volts)

class UsbTestTerminal(object):
    VREF_CAL_POS = 0
    TEMP30_CAL_POS = 1
    TEMP110_CAL_POS = 2
    ADC_KEY_POS = 3
    ADC_PA3_POS = 4
    ADC_TEMP_POS = 5
    ADC_VREF_POS = 6

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
        self._move=[]

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

    def move(self,x,y,laserPower):
        self._move=[x,y,laserPower]
        self._usb.send(MoveMessage(x,y,laserPower))

    def set_drips(self,dripCount=0):
        self._usb.send(SetDripCountMessage(dripCount))

    def identify(self):
        self._usb.send(IdentifyMessage())

    def enter_bootloader(self):
        self._usb.send(EnterBootloaderMessage())
        if (self._verbose):
            print "Bootloadereded"

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
            [adcNum,adcVrefCal] = self.get_adc_val(self.VREF_CAL_POS)
            [adcNum,adcTemp30] = self.get_adc_val(self.TEMP30_CAL_POS)
            [adcNum,adcTemp110] = self.get_adc_val(self.TEMP110_CAL_POS)
            self._adcCals = [adcVrefCal,adcTemp30,adcTemp110]

    def get_temperature(self):

        self.get_adc_calibrations()

        #Return actual Temperature in C
        #Formulas taken from STM32F0 datasheet page 252
        adcVrefCal = self._adcCals[self.VREF_CAL_POS]
        adcTemp30 = self._adcCals[self.TEMP30_CAL_POS]
        adcTemp110 = self._adcCals[self.TEMP110_CAL_POS]

        #Get the current Vref and Temperature each time
        [adcNum,adcTemperature]=self.get_adc_val(self.ADC_TEMP_POS)
        [adcNum,adcVref]=self.get_adc_val(self.ADC_VREF_POS)

        vrefCompensation = 1.0*adcVrefCal/adcVref
        temperature = adcTemperature*vrefCompensation-adcTemp30
        temperature = temperature*(110-30)/(adcTemp110-adcTemp30)
        temperature = temperature + 30

        if (self._verbose):
            print ('Temperatures Value={0} Celcius={1}'.format(adcTemperature,temperature))

        return temperature

    def get_supply_voltage(self):

        self.get_adc_calibrations()
        adcVrefCal=self._adcCals[self.VREF_CAL_POS]
        [adcNum,adcVref]=self.get_adc_val(self.ADC_VREF_POS)

        vrefCompensation = 1.0*adcVrefCal/adcVref
        
        #calibrated at 3.3V always
        supplyVoltage = 3.3*vrefCompensation

        if (self._verbose):
            print ('Voltage {0}, Value {1}'.format(supplyVoltage,adcVref))

        return supplyVoltage

    def get_adc_key_val(self):
        return self.get_adc_val(self.ADC_KEY_POS)

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

def test_adc_key(t):
    key_min=4095
    key_max=0
    while(1):
        adcKeyVal = t.get_adc_key_val()
        if adcKeyVal[1]>key_max:
            key_max=adcKeyVal[1]
        if adcKeyVal[1]<key_min:
            key_min=adcKeyVal[1]

        #print "Voltage: {0} V, Temperature {1} oC".format(voltage,temperature)
        print "Adc Key Value: {0} Max: {1} Min: {2}".format(adcKeyVal,key_max,key_min)
        time.sleep(1)

if __name__ == '__main__':
    t = UsbTestTerminal(verbose=False); 
    t.identify()
    t.set_drips(0)
    t.enter_bootloader()
    #test_adc_key(t)
    while(1): 
        print "Voltage: {0} Temperature {1}".format(t.get_supply_voltage(), t.get_temperature())
        adcKeyVal = t.get_adc_key_val()
        print "Adc Key Value: {0}".format(adcKeyVal)
        time.sleep(0.1)






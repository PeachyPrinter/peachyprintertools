#!/usr/bin/python
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from peachyprinter.infrastructure.communicator import UsbPacketCommunicator
from peachyprinter.infrastructure.messages import *


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
        self._move=[0,0,0]

        self._usb = UsbPacketCommunicator(10)
        self._usb.register_handler(IAmMessage, self.iAmHandler)
        self._usb.register_handler(DripRecordedMessage, self.dripHandler)
        self._usb.register_handler(ReturnAdcValMessage, self.adcHandler)
        self._usb.start()
        if verbose:
            print "Started usb terminal"
        time.sleep(0.1)

    def usbClose(self):
        self._usb.close()

    def laserOff(self):
        move=self._move
        self._usb.send(MoveMessage(move[0],move[1],0))

    def laserOn(self):
        move=self._move
        self._usb.send(MoveMessage(move[0],move[1],255))

    def move(self,x,y,laserPower=0):
        self._move=[x,y,laserPower]
        self._usb.send(MoveMessage(x,y,laserPower))

    def setDrips(self,dripCount=0):
        self._usb.send(SetDripCountMessage(dripCount))

    def identify(self):
        self._usb.send(IdentifyMessage())

    def enterBootloader(self,i_am_sure=None):
        if i_am_sure==(0xDEADBEEF):
            self._usb.send(EnterBootloaderMessage())
            if (self._verbose):
                print "Bootloadereded"
        elif (self._verbose):
            print "i_am_sure not loaded with the correct value"
            print "Note: This may lock your peachy into the bootloader"
            print "      if you have old firmware on your board"

    #A non-ideal push/pop queue interface.
    #Doesn't account for mis-matching - May be worth clearing on each request?
    def popAdc(self,timeout=0.1):
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

    def clearAdcQueues(self):
        self._adcNum=[]
        self._adcVal=[]

    def getAdcCalibrations(self):
        if len(self._adcCals)!=3:
            [adcNum,adcVrefCal] = self.getAdcVal(self.VREF_CAL_POS)
            [adcNum,adcTemp30] = self.getAdcVal(self.TEMP30_CAL_POS)
            [adcNum,adcTemp110] = self.getAdcVal(self.TEMP110_CAL_POS)
            self._adcCals = [adcVrefCal,adcTemp30,adcTemp110]

    def getTemperature(self):

        self.getAdcCalibrations()

        #Return actual Temperature in C
        #Formulas taken from STM32F0 datasheet page 252
        adcVrefCal = self._adcCals[self.VREF_CAL_POS]
        adcTemp30 = self._adcCals[self.TEMP30_CAL_POS]
        adcTemp110 = self._adcCals[self.TEMP110_CAL_POS]

        #Get the current Vref and Temperature each time
        [adcNum,adcTemperature]=self.getAdcVal(self.ADC_TEMP_POS)
        [adcNum,adcVref]=self.getAdcVal(self.ADC_VREF_POS)

        vrefCompensation = 1.0*adcVrefCal/adcVref
        temperature = adcTemperature*vrefCompensation-adcTemp30
        temperature = temperature*(110-30)/(adcTemp110-adcTemp30)
        temperature = temperature + 30

        if (self._verbose):
            print ('Temperatures Value={0} Celcius={1}'.format(adcTemperature,temperature))

        return temperature

    def getSupplyVoltage(self):

        self.getAdcCalibrations()
        adcVrefCal=self._adcCals[self.VREF_CAL_POS]
        [adcNum,adcVref]=self.getAdcVal(self.ADC_VREF_POS)

        vrefCompensation = 1.0*adcVrefCal/adcVref
        
        #calibrated at 3.3V always
        supplyVoltage = 3.3*vrefCompensation

        if (self._verbose):
            print ('Voltage {0}, Value {1}'.format(supplyVoltage,adcVref))

        return supplyVoltage

    def getAdcKeyVal(self):
        return self.getAdcVal(self.ADC_KEY_POS)

    def getAdcVal(self,adcNum):
        '''ADC NUMBERS:
        0 - Vref Calibration Factor
        1 - 30C temperature calibration
        2 - 110C temperature calibration
        3 - ADC key (PA2)
        4 - Pin (PA3)
        5 - Temperature
        6 - Vref (3.3V volts)
        '''

        self._adcNum.append(adcNum)
        self._usb.send(GetAdcValMessage(adcNum))
        if self._verbose:
            print('adcNum: {0}'.format(adcNum))
        return self.popAdc()

    def adcHandler(self,message):
        if (len(self._adcNum) > len(self._adcVal)):
            self._adcVal.append(message.adcVal)
            if self._verbose:
                print('adcNum: {0} adcVal: {1}'.format(self._adcNum[-1], self._adcVal[-1]))
        else:
            self.clearAdcQueues()

    def dripHandler(self, message):
        self._drips=message.drips
        if self._verbose:
            print('Recieved drip: {0}'.format(message.drips))

    def iAmHandler(self, message):
        self._serial=message.sn
        self._swrev=message.swrev
        self._hwrev=message.hwrev
        self._dataRate=message.dataRate
        if self._verbose:
            print('Serial number: {0}'.format(message.sn))
            print('SW rev number: {0}'.format(message.swrev))
            print('HW rev number: {0}'.format(message.hwrev))
            print('Data Rate:     {0}'.format(message.dataRate))

def testAdcKey(t):
    key_min=4095
    key_max=0
    while(1):
        adcKeyVal = t.getAdcKeyVal()
        if adcKeyVal[1]>key_max:
            key_max=adcKeyVal[1]
        if adcKeyVal[1]<key_min:
            key_min=adcKeyVal[1]

        print "Adc Key Value: {0} Max: {1} Min: {2}".format(adcKeyVal,key_max,key_min)
        time.sleep(1)

if __name__ == '__main__':
    t = UsbTestTerminal(verbose=True); 
    t.identify()
    t.setDrips(0)
    while(1): 
        print "Voltage: {0} Temperature {1}".format(t.getSupplyVoltage(), t.getTemperature())
        adcKeyVal = t.getAdcKeyVal()
        print "Adc Key Value: {0}".format(adcKeyVal)
        time.sleep(1)






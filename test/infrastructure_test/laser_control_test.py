import unittest
import mock
import numpy
import test_helpers
import math

from infrastructure.laser_control import AudioModulationLaserControl

class AudioModulationLaserControlTests(unittest.TestCase, test_helpers.TestHelpers):
    sample_rate = 1000
    on_frequency = sample_rate / 4
    off_frequency = sample_rate / 8
        
    def test_when_laser_off_modulate_it_at_off_frequency(self):
        laser_control = AudioModulationLaserControl(self.sample_rate,self.on_frequency,self.off_frequency)
        laser_control.set_laser_off()
        sample_data_chunk = numpy.array([(0,0)])
        po1 = math.cos(0.0 / 8.0 * 2.0 * math.pi)
        po2 = math.cos(1.0 / 8.0 * 2.0 * math.pi)
        po3 = math.cos(2.0 / 8.0 * 2.0 * math.pi)
        po4 = math.cos(3.0 / 8.0 * 2.0 * math.pi)
        po5 = math.cos(4.0 / 8.0 * 2.0 * math.pi)
        po6 = math.cos(5.0 / 8.0 * 2.0 * math.pi)
        po7 = math.cos(6.0 / 8.0 * 2.0 * math.pi)
        po8 = math.cos(7.0 / 8.0 * 2.0 * math.pi)
        expected_data = numpy.array([(po1,po1),(po2,po2),(po3,po3),(po4,po4),(po5,po5),(po6,po6),(po7,po7),(po8,po8)])
        
        actual_data =  list(laser_control.modulate(sample_data_chunk))

        self.assertNumpyArrayEquals(expected_data,actual_data)

    def test_when_laser_on_modulate_it_at_on_frequency(self):
        laser_control = AudioModulationLaserControl(self.sample_rate,self.on_frequency,self.off_frequency)
        laser_control.set_laser_on()
        sample_data_chunk = numpy.array([(0,0)])
        po1 = math.cos((0.0 / 4.0) * 2.0 * math.pi)
        po2 = math.cos((1.0 / 4.0) * 2.0 * math.pi)
        po3 = math.cos((2.0 / 4.0) * 2.0 * math.pi)
        po4 = math.cos((3.0 / 4.0) * 2.0 * math.pi)
        po5 = math.cos((0.0 / 4.0) * 2.0 * math.pi)
        po6 = math.cos((1.0 / 4.0) * 2.0 * math.pi)
        po7 = math.cos((2.0 / 4.0) * 2.0 * math.pi)
        po8 = math.cos((3.0 / 4.0) * 2.0 * math.pi)
        expected_data = numpy.array([(po1,po1),(po2,po2),(po3,po3),(po4,po4),(po5,po5),(po6,po6),(po7,po7),(po8,po8)])
        
        actual_data =  list(laser_control.modulate(sample_data_chunk))

        self.assertNumpyArrayEquals(expected_data,actual_data)

    def test_on_frequency_must_be_an_even_divisor_of_sample_rate(self):
        sample_rate = 1000
        bad_on_frequency = 71
        off_frequency = 125
        with self.assertRaises(Exception):
            AudioModulationLaserControl(sample_rate,bad_on_frequency,off_frequency)

    def test_off_frequency_must_be_an_even_divisor_of_sample_rate(self):
        sample_rate = 1000
        on_frequency = 500
        bad_off_frequency = 99
        with self.assertRaises(Exception):
            AudioModulationLaserControl(sample_rate,on_frequency,bad_off_frequency)

    def test_number_of_sample_generated_for_on_and_off_should_be_consistant(self):
        sample_rate = 44100
        on_frequency = 11025
        off_frequency = 7350
        sample_data_chunk = numpy.array([(0,0)])

        laser_control = AudioModulationLaserControl(sample_rate,on_frequency,off_frequency)
        laser_control.set_laser_on()
        laser_on = len(list(laser_control.modulate(sample_data_chunk)))
        laser_control.set_laser_off()
        laser_off = len(list(laser_control.modulate(sample_data_chunk)))

        self.assertEqual(laser_on,laser_off)


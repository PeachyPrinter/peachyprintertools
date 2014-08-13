import numpy
import unittest
from domain.commands import *
from infrastructure.configuration import ConfigurationGenerator

class NumpyTestHelpers(object):

    def assertNumpyArrayEquals(self,array1, array2):
        equal = numpy.array_equal(array1,array2)
        if not equal:
            self.fail("\n%s\ndid not equal\n%s" % (str(array1),str(array2)))

    def assertNumpyArrayClose(self,array1, array2):
        equal = numpy.allclose(array1,array2)
        if not equal:
            self.fail("\n%s\ndid not equal\n%s" % (str(array1),str(array2)))

class CommandTestHelpers(object):

    def almostEqual(self,a, b,tollerence = 0.0001):
        diff = a - b
        return abs(diff) < tollerence 

    def coordantesAlmostEqual(self,point_a, point_b,tollerence = 0.0001):
        return self.almostEqual(point_a[0] , point_b[0]) and self.almostEqual(point_a[1] , point_b[1])

    def assertLateralDrawEqual(self, command1, command2):
        if not self.coordantesAlmostEqual(command1.start, command2.start):
            self.fail("Command starts do not match\n%s\ndid not equal\n%s" % (command1, command2))
        if not self.coordantesAlmostEqual(command1.end,command2.end):
            self.fail("Command ends do not match\n%s\ndid not equal\n%s" % (command1, command2))
        if not self.almostEqual(command1.speed, command2.speed):
            self.fail("Command speeds do not match\n%s\ndid not equal\n%s" % (command1, command2))

    def assertLateralMoveEqual(self, command1, command2):
        self.assertLateralDrawEqual(command1, command2)

    def assertVerticleMoveEqual(self, command1, command2):
        if not (self._equal(command1.start, command2.start) and self._equal(command1.end, command2.end) and self._equal(command1.speed, command2.speed)):
            self.fail("Commands do not match\n%s\ndid not equal\n%s" % (command1, command2))

    def assertCommandEqual(self, command1, command2):
        if type(command1) != type(command2):
            self.fail("Command did not match\n%s\ndid not equal\n%s" % (str(command1), str(command2)))
        if type(command1) == LateralDraw:
            self.assertLateralDrawEqual(command1,command2)
        elif type(command1) == LateralMove:
            self.assertLateralMoveEqual(command1,command2)
        elif type(command1) == VerticalMove:
            self.assertVerticleMoveEqual(command1,command2)
        else:
            self.fail("Test Helper Unsupported type: %s" % type(command1) )

    def assertCommandsEqual(self, commands1, commands2):
        if len(commands1) != len(commands2):
            self.fail("Commands do not match\n%s\ndid not equal\n%s" % (self._stringify(commands1), self._stringify(commands2)))
        for i in range(0, len(commands1)):
            try:
                self.assertCommandEqual(commands1[i],commands2[i])
            except Exception as ex:
                self.fail("Commands do not match\n%s\ndid not equal\n%s\nDetail: %s" % (self._stringify(commands1), self._stringify(commands2), ex.message))

    def assertLayerEquals(self,layer1,layer2):
        if self.assertAlmostEqual(layer1.z, layer2.z):
            self.fail("z do not match %s did not equal %s" % (layer1.z, layer2.z))
        self.assertCommandsEqual(layer1.commands,layer2.commands)
    
    def assertLayersEquals(self,layers1,layers2):
        if len(layers1) != len(layers2):
            self.fail("Count of Layers do not match\n%s\ndid not equal\n%s" % (self._stringify(layers1), self._stringify(layers2)))
        for i in range(len(layers1)):
            self.assertLayerEquals(layers1[i],layers2[i])

    def _stringify(self,list_data):
        return [str(element) for element in list_data]

    def _equal(self,a,b, tol = 0.0001):
        return abs(a-b) <= (abs(a)+abs(b))/2 * tol

class DefaultsHelpers(object):
    @property
    def default_config(self):
        return ConfigurationGenerator().default_configuration()

class TestHelpers(NumpyTestHelpers,CommandTestHelpers, DefaultsHelpers):
    def assertListDict(self,expected,actual):
        self.assertEquals(len(expected), len(actual))
        for item in expected:
            if not item in actual:
                self.fail("%s\ndid not equal\n%s\non item\n%s" % (expected,actual, item))

    def assertListContentsEqual(self,expected,actual):
        self.assertEquals(len(expected), len(actual))
        for index in range(0, len(expected)):
            self.assertEquals(str(expected[index]),str(actual[index]), '%s != %s' %(expected[index], actual[index]))

    def assertConfigurationEqual(self, expected, actual):
        self.assertEquals(type(expected), type(actual), 'Not a config was %s and %s' % (type(expected), type(actual)))
        self.assertEquals(expected.name                                 , actual.name                                 , "name did not match expected %s was %s"                                  % (expected.name                                 , actual.name                                 ))
        self.assertEquals(expected.audio.output.bit_depth               , actual.audio.output.bit_depth               , "audio.output.bit_depth did not match expected %s was %s"                % (expected.audio.output.bit_depth               , actual.audio.output.bit_depth               ))
        self.assertEquals(expected.audio.output.sample_rate             , actual.audio.output.sample_rate             , "audio.output.sample_rate did not match expected %s was %s"              % (expected.audio.output.sample_rate             , actual.audio.output.sample_rate             ))
        self.assertEquals(expected.audio.output.modulation_on_frequency , actual.audio.output.modulation_on_frequency , "audio.output.modulation_on_frequency did not match expected %s was %s"  % (expected.audio.output.modulation_on_frequency , actual.audio.output.modulation_on_frequency ))
        self.assertEquals(expected.audio.output.modulation_off_frequency, actual.audio.output.modulation_off_frequency, "audio.output.modulation_off_frequency did not match expected %s was %s" % (expected.audio.output.modulation_off_frequency, actual.audio.output.modulation_off_frequency))
        self.assertEquals(expected.audio.input.bit_depth                , actual.audio.input.bit_depth                , "audio.input.bit_depth did not match expected %s was %s"                 % (expected.audio.input.bit_depth                , actual.audio.input.bit_depth                ))
        self.assertEquals(expected.audio.input.sample_rate              , actual.audio.input.sample_rate              , "audio.input.sample_rate did not match expected %s was %s"               % (expected.audio.input.sample_rate              , actual.audio.input.sample_rate              ))

        self.assertEquals(expected.calibration.max_deflection           , actual.calibration.max_deflection           , "calibration.max_deflection did not match expected %s was %s"            % (expected.calibration.max_deflection           , actual.calibration.max_deflection           ))
        self.assertEquals(expected.calibration.height                   , actual.calibration.height                   , "calibration.height did not match expected %s was %s"                    % (expected.calibration.height                   , actual.calibration.height                   ))
        self.assertEquals(expected.calibration.lower_points             , actual.calibration.lower_points             , "calibration.lower_points did not match expected %s was %s"              % (expected.calibration.lower_points             , actual.calibration.lower_points             ))
        self.assertEquals(expected.calibration.upper_points             , actual.calibration.upper_points             , "calibration.upper_points did not match expected %s was %s"              % (expected.calibration.upper_points             , actual.calibration.upper_points             ))

        self.assertEquals(expected.options.draw_speed                   , actual.options.draw_speed                   , "options.draw_speed did not match expected %s was %s"                    % (expected.options.draw_speed                   , actual.options.draw_speed                   ))
        self.assertEquals(expected.options.scaling_factor               , actual.options.scaling_factor               , "options.scaling_factor did not match expected %s was %s"                % (expected.options.scaling_factor               , actual.options.scaling_factor               ))
        self.assertEquals(expected.options.laser_offset                 , actual.options.laser_offset                 , "options.laser_offset did not match expected %s was %s"                  % (expected.options.laser_offset                 , actual.options.laser_offset                 ))
        self.assertEquals(expected.options.sublayer_height_mm           , actual.options.sublayer_height_mm           , "options.sublayer_height_mm did not match expected %s was %s"            % (expected.options.sublayer_height_mm           , actual.options.sublayer_height_mm           ))
        self.assertEquals(expected.options.laser_thickness_mm           , actual.options.laser_thickness_mm           , "options.laser_thickness_mm did not match expected %s was %s"            % (expected.options.laser_thickness_mm           , actual.options.laser_thickness_mm           ))
        self.assertEquals(expected.options.overlap_amount              , actual.options.overlap_amount                , "options.overlap_amount did not match expected %s was %s"                % (expected.options.overlap_amount               , actual.options.overlap_amount               ))
        self.assertEquals(expected.options.use_shufflelayers           , actual.options.use_shufflelayers             , "options.use_shufflelayers did not match expected %s was %s"             % (expected.options.use_shufflelayers            , actual.options.use_shufflelayers            ))
        self.assertEquals(expected.options.use_sublayers               , actual.options.use_sublayers                 , "options.use_sublayers did not match expected %s was %s"                 % (expected.options.use_sublayers                , actual.options.use_sublayers                ))
        self.assertEquals(expected.options.use_overlap                 , actual.options.use_overlap                   , "options.use_overlap did not match expected %s was %s"                   % (expected.options.use_overlap                  , actual.options.use_overlap                  ))
        self.assertEquals(expected.options.print_queue_delay           , actual.options.print_queue_delay             , "options.print_queue_delay did not match expected %s was %s"             % (expected.options.print_queue_delay            , actual.options.print_queue_delay            ))
        self.assertEquals(expected.options.pre_layer_delay             , actual.options.pre_layer_delay               , "options.pre_layer_delay did not match expected %s was %s"               % (expected.options.pre_layer_delay              , actual.options.pre_layer_delay              ))


        self.assertEquals(expected.dripper.max_lead_distance_mm         , actual.dripper.max_lead_distance_mm         , "dripper.max_lead_distance_mm did not match expected %s was %s"          % (expected.dripper.max_lead_distance_mm         , actual.dripper.max_lead_distance_mm         ))
        self.assertEquals(expected.dripper.drips_per_mm                 , actual.dripper.drips_per_mm                 , "dripper.drips_per_mm did not match expected %s was %s"                  % (expected.dripper.drips_per_mm                 , actual.dripper.drips_per_mm                 ))
        self.assertEquals(expected.dripper.photo_zaxis_delay            , actual.dripper.photo_zaxis_delay            , "dripper.photo_zaxis_delay did not match expected %s was %s"             % (expected.dripper.photo_zaxis_delay            , actual.dripper.photo_zaxis_delay            ))

        self.assertEquals(expected.serial.on                            , actual.serial.on                            , "serial.on did not match expected %s was %s"                             % (expected.serial.on                            , actual.serial.on                            ))
        self.assertEquals(expected.serial.port                          , actual.serial.port                          , "serial.port did not match expected %s was %s"                           % (expected.serial.port                          , actual.serial.port                          ))
        self.assertEquals(expected.serial.on_command                    , actual.serial.on_command                    , "serial.on_command did not match expected %s was %s"                     % (expected.serial.on_command                    , actual.serial.on_command                    ))
        self.assertEquals(expected.serial.off_command                   , actual.serial.off_command                   , "serial.off_command did not match expected %s was %s"                    % (expected.serial.off_command                   , actual.serial.off_command                   ))
        self.assertEquals(expected.serial.layer_started                 , actual.serial.layer_started                 , "serial.layer_started did not match expected %s was %s"                  % (expected.serial.layer_started                 , actual.serial.layer_started                 ))
        self.assertEquals(expected.serial.layer_ended                   , actual.serial.layer_ended                   , "serial.layer_ended did not match expected %s was %s"                    % (expected.serial.layer_ended                   , actual.serial.layer_ended                   ))
        self.assertEquals(expected.serial.print_ended                   , actual.serial.print_ended                   , "serial.print_ended did not match expected %s was %s"                    % (expected.serial.print_ended                   , actual.serial.print_ended                   ))
        
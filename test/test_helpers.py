import numpy
import unittest
from peachyprinter.domain.commands import *
from peachyprinter.infrastructure.configuration import ConfigurationGenerator

class NumpyTestHelpers(object):

    def assertNumpyArrayEquals(self,array1, array2):
        equal = numpy.array_equal(array1,array2)
        if not equal:
            self.fail("\n%s\ndid not equal\n%s" % (array1.shape,array2.shape))

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

        self.assertEquals(expected.calibration.max_deflection           , actual.calibration.max_deflection           , "calibration.max_deflection did not match expected %s was %s"            % (expected.calibration.max_deflection           , actual.calibration.max_deflection           ))
        self.assertEquals(expected.calibration.height                   , actual.calibration.height                   , "calibration.height did not match expected %s was %s"                    % (expected.calibration.height                   , actual.calibration.height                   ))
        self.assertEquals(expected.calibration.lower_points             , actual.calibration.lower_points             , "calibration.lower_points did not match expected %s was %s"              % (expected.calibration.lower_points             , actual.calibration.lower_points             ))
        self.assertEquals(expected.calibration.upper_points             , actual.calibration.upper_points             , "calibration.upper_points did not match expected %s was %s"              % (expected.calibration.upper_points             , actual.calibration.upper_points             ))
        self.assertEquals(expected.calibration.print_area_x             , actual.calibration.print_area_x             , "calibration.print_area_x did not match expected %s was %s"              % (expected.calibration.print_area_x             , actual.calibration.print_area_x             ))
        self.assertEquals(expected.calibration.print_area_y             , actual.calibration.print_area_y             , "calibration.print_area_y did not match expected %s was %s"              % (expected.calibration.print_area_y             , actual.calibration.print_area_y             ))
        self.assertEquals(expected.calibration.print_area_z             , actual.calibration.print_area_z             , "calibration.print_area_z did not match expected %s was %s"              % (expected.calibration.print_area_z             , actual.calibration.print_area_z             ))
        self.assertEquals(expected.calibration.flip_x_axis              , actual.calibration.flip_x_axis              , "calibration.flip_x_axis did not match expected %s was %s"               % (expected.calibration.flip_x_axis              , actual.calibration.flip_x_axis              ))
        self.assertEquals(expected.calibration.flip_y_axis              , actual.calibration.flip_y_axis              , "calibration.flip_y_axis did not match expected %s was %s"               % (expected.calibration.flip_y_axis              , actual.calibration.flip_y_axis              ))
        self.assertEquals(expected.calibration.swap_axis                , actual.calibration.swap_axis                , "calibration.swap_axis did not match expected %s was %s"                 % (expected.calibration.swap_axis                , actual.calibration.swap_axis                ))

        self.assertEquals(expected.options.scaling_factor               , actual.options.scaling_factor               , "options.scaling_factor did not match expected %s was %s"                % (expected.options.scaling_factor               , actual.options.scaling_factor               ))
        self.assertEquals(expected.options.sublayer_height_mm           , actual.options.sublayer_height_mm           , "options.sublayer_height_mm did not match expected %s was %s"            % (expected.options.sublayer_height_mm           , actual.options.sublayer_height_mm           ))
        self.assertEquals(expected.options.laser_thickness_mm           , actual.options.laser_thickness_mm           , "options.laser_thickness_mm did not match expected %s was %s"            % (expected.options.laser_thickness_mm           , actual.options.laser_thickness_mm           ))
        self.assertEquals(expected.options.overlap_amount              , actual.options.overlap_amount                , "options.overlap_amount did not match expected %s was %s"                % (expected.options.overlap_amount               , actual.options.overlap_amount               ))
        self.assertEquals(expected.options.use_shufflelayers           , actual.options.use_shufflelayers             , "options.use_shufflelayers did not match expected %s was %s"             % (expected.options.use_shufflelayers            , actual.options.use_shufflelayers            ))
        self.assertEquals(expected.options.use_sublayers               , actual.options.use_sublayers                 , "options.use_sublayers did not match expected %s was %s"                 % (expected.options.use_sublayers                , actual.options.use_sublayers                ))
        self.assertEquals(expected.options.use_overlap                 , actual.options.use_overlap                   , "options.use_overlap did not match expected %s was %s"                   % (expected.options.use_overlap                  , actual.options.use_overlap                  ))
        self.assertEquals(expected.options.print_queue_delay           , actual.options.print_queue_delay             , "options.print_queue_delay did not match expected %s was %s"             % (expected.options.print_queue_delay            , actual.options.print_queue_delay            ))
        self.assertEquals(expected.options.pre_layer_delay             , actual.options.pre_layer_delay               , "options.pre_layer_delay did not match expected %s was %s"               % (expected.options.pre_layer_delay              , actual.options.pre_layer_delay              ))
        self.assertEquals(expected.options.shuffle_layers_amount       , actual.options.shuffle_layers_amount         , "options.shuffle_layers_amount did not match expected %s was %s"         % (expected.options.shuffle_layers_amount        , actual.options.shuffle_layers_amount        ))
        self.assertEquals(expected.options.post_fire_delay             , actual.options.post_fire_delay               , "options.post_fire_delay did not match expected %s was %s"               % (expected.options.post_fire_delay              , actual.options.post_fire_delay              ))
        self.assertEquals(expected.options.slew_delay                  , actual.options.slew_delay                    , "options.slew_delay      did not match expected %s was %s"               % (expected.options.slew_delay                   , actual.options.slew_delay                   ))
        self.assertEquals(expected.options.write_wav_files             , actual.options.write_wav_files               , "options.write_wav_files did not match expected %s was %s"               % (expected.options.write_wav_files              , actual.options.write_wav_files              ))
        self.assertEquals(expected.options.write_wav_files_folder      , actual.options.write_wav_files_folder        , "options.write_wav_files_folder did not match expected %s was %s"        % (expected.options.write_wav_files_folder       , actual.options.write_wav_files_folder       ))

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

        self.assertEquals(expected.email.on                             , actual.email.on                             , "email.on did not match expected %s was %s"                              % (expected.email.on                             , actual.email.on                             ))
        self.assertEquals(expected.email.port                           , actual.email.port                           , "email.port did not match expected %s was %s"                            % (expected.email.port                           , actual.email.port                           ))
        self.assertEquals(expected.email.host                           , actual.email.host                           , "email.host did not match expected %s was %s"                            % (expected.email.host                           , actual.email.host                           ))
        self.assertEquals(expected.email.sender                         , actual.email.sender                         , "email.sender did not match expected %s was %s"                          % (expected.email.sender                         , actual.email.sender                         ))
        self.assertEquals(expected.email.recipient                      , actual.email.recipient                      , "email.recipient did not match expected %s was %s"                       % (expected.email.recipient                      , actual.email.recipient                      ))
        self.assertEquals(expected.email.username                       , actual.email.username                       , "email.username  did not match expected %s was %s"                       % (expected.email.username                       , actual.email.username                       ))
        self.assertEquals(expected.email.password                       , actual.email.password                       , "email.password  did not match expected %s was %s"                       % (expected.email.password                       , actual.email.password                       ))

        self.assertEquals(expected.cure_rate.base_height                , actual.cure_rate.base_height                , "cure_rate.base_height did not match expected %s was %s"                 % (expected.cure_rate.base_height                , actual.cure_rate.base_height                ))
        self.assertEquals(expected.cure_rate.total_height               , actual.cure_rate.total_height               , "cure_rate.total_height did not match expected %s was %s"                % (expected.cure_rate.total_height               , actual.cure_rate.total_height               ))
        self.assertEquals(expected.cure_rate.start_speed                , actual.cure_rate.start_speed                , "cure_rate.start_speed did not match expected %s was %s"                 % (expected.cure_rate.start_speed                , actual.cure_rate.start_speed                ))
        self.assertEquals(expected.cure_rate.finish_speed               , actual.cure_rate.finish_speed               , "cure_rate.finish_speed did not match expected %s was %s"                % (expected.cure_rate.finish_speed               , actual.cure_rate.finish_speed               ))
        self.assertEquals(expected.cure_rate.draw_speed                 , actual.cure_rate.draw_speed                 , "cure_rate.draw_speed did not match expected %s was %s"                  % (expected.cure_rate.draw_speed                 , actual.cure_rate.draw_speed                 ))
        self.assertEquals(expected.cure_rate.move_speed                 , actual.cure_rate.move_speed                 , "cure_rate.move_speed did not match expected %s was %s"                  % (expected.cure_rate.move_speed                 , actual.cure_rate.move_speed                 ))
        self.assertEquals(expected.cure_rate.use_draw_speed             , actual.cure_rate.use_draw_speed             , "cure_rate.use_draw_speed did not match expected %s was %s"              % (expected.cure_rate.use_draw_speed             , actual.cure_rate.use_draw_speed             ))
        self.assertEquals(expected.cure_rate.override_laser_power       , actual.cure_rate.override_laser_power       , "cure_rate.override_laser_poweratch expected %s was %s"                  % (expected.cure_rate.override_laser_power       , actual.cure_rate.override_laser_power       ))
        self.assertEquals(expected.cure_rate.override_laser_power_amount, actual.cure_rate.override_laser_power_amount, "cure_rate.override_laser_power_amounth expected %s was %s"              % (expected.cure_rate.override_laser_power_amount, actual.cure_rate.override_laser_power_amount))

        self.assertEqual(expected.circut.software_revision              , actual.circut.software_revision             , "circut.software_revision did not march expected %s was %s"              % (expected.circut.software_revision            ,  actual.circut.software_revision             ))
        self.assertEqual(expected.circut.hardware_revision              , actual.circut.hardware_revision             , "circut.hardware_revision did not march expected %s was %s"              % (expected.circut.hardware_revision            ,  actual.circut.hardware_revision             ))
        self.assertEqual(expected.circut.serial_number                  , actual.circut.serial_number                 , "circut.serial_number did not march expected %s was %s"                  % (expected.circut.serial_number                ,  actual.circut.serial_number                 ))
        self.assertEqual(expected.circut.data_rate                      , actual.circut.data_rate                     , "circut.data_rate did not march expected %s was %s"                      % (expected.circut.data_rate                    ,  actual.circut.data_rate                     ))
        self.assertEqual(expected.circut.print_queue_length             , actual.circut.print_queue_length            , "circut.print_queue_length did not march expected %s was %s"             % (expected.circut.print_queue_length           ,  actual.circut.print_queue_length            ))
        self.assertEqual(expected.circut.calibration_queue_length       , actual.circut.calibration_queue_length      , "circut.calibration_queue_length did not march expected %s was %s"       % (expected.circut.calibration_queue_length     ,  actual.circut.calibration_queue_length      ))

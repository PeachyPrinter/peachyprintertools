import unittest
import numpy as np 
import math
from math import pi
import os
import sys
from mock import MagicMock, patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.simulator import *

class TestHelp(object):
    epsilon = 0.000001
    def assertProjectiveCoordinatesEqual(self, a,b):
        for i in range(3):
            diff = a[0,i]/a[0,3] - b[0,i]/b[0,3]
            self.assertTrue(abs(diff)<self.epsilon, 'Was out by : %s' % diff)

# class MirrorTest(unittest.TestCase,TestHelp):
#     def test_reflect_refects_at_origin_when_perpendicular_to_origin(self):
#         base_point = np.matrix([0.0,0.0,0.0,1.0])
#         point = np.matrix([0.0,0.0,2.0,1.0])
#         expected_point = np.matrix([0.0,0.0,-2.0,1.0])
#         normal =  np.matrix([0.0,0.0,1.0,0.0])
#         axis =  np.matrix([0.0,1.0,0.0,0.0])
#         galvo_pos = MagicMock()
#         galvo_pos.return_value = 0

#         mirror = Mirror(base_point, normal, axis, galvo_pos)

#         result = mirror.reflect(point, 0.0)

#         self.assertProjectiveCoordinatesEqual(expected_point,result)

#     def test_reflect_refects(self):
#         base_point = np.matrix([0.0,0.0,0.0,1.0])
#         point = np.matrix([1.0,0.0,3.0,1.0])
#         expected_point = np.matrix([-3.0,0.0,-1.0,1.0])
#         normal = np.matrix([math.sqrt(2)/2,0.0,math.sqrt(2)/2,0.0])
#         axis =  np.matrix([-1.0,0.0,-1.0,0.0])
#         galvo_pos = MagicMock()
#         galvo_pos.return_value = 0

#         mirror = Mirror(base_point, normal, axis, galvo_pos)
        
#         result = mirror.reflect(point, 0.0)

#         self.assertProjectiveCoordinatesEqual(expected_point,result)

#     def test_normal_can_be_non_unit(self):
#         base_point = np.matrix([0.0,0.0,0.0,1.0])
#         point = np.matrix([1.0,0.0,3.0,1.0])
#         expected_point = np.matrix([-3.0,0.0,-1.0,1.0])
#         normal = np.matrix([1.0,0.0,1.0,0.0])
#         axis =  np.matrix([-1.0,0.0,-1.0,0.0])
#         galvo_pos = MagicMock()
#         galvo_pos.return_value = 0

#         mirror = Mirror(base_point, normal, axis, galvo_pos)
        
#         result = mirror.reflect(point, 0.0)

#         self.assertProjectiveCoordinatesEqual(expected_point,result)

#     def test_reflect_refects_not_at_origin_when_perpendicular_to_the_point(self):
#         base_point = np.matrix([0.0,0.0,1.0,1.0])
#         point = np.matrix([0.0,0.0,2.0,1.0])
#         expected_point = np.matrix([0.0,0.0,-0.0,1.0])
#         normal =  np.matrix([0.0,0.0,1.0,0.0])
#         axis =  np.matrix([1.0,0.0,0.0,0.0])
#         galvo_pos = MagicMock()
#         galvo_pos.return_value = 0

#         mirror = Mirror(base_point, normal, axis, galvo_pos)

#         result = mirror.reflect(point, 0.0)

#         self.assertProjectiveCoordinatesEqual(expected_point,result)

#     def test_reflect_refects_not_at_origin_when_not_perpendicular_to_the_point(self):
#         base_point = np.matrix([0.0,0.0,1.0,1.0])
#         point = np.matrix([0.0,10.0,2.0,1.0])
#         expected_point = np.matrix([0.0,10.0,-0.0,1.0])
#         normal =  np.matrix([0.0,0.0,1.0,0.0])
#         axis =  np.matrix([0.0,1.0,0.0,0.0])
#         galvo_pos = MagicMock()
#         galvo_pos.return_value = 0

#         mirror = Mirror(base_point, normal,axis, galvo_pos)

#         result = mirror.reflect(point, 0.0)

#         self.assertProjectiveCoordinatesEqual(expected_point,result)

#     def test_mirror_calculates_angle_correctly(self):
#         base_point = np.matrix([0.0,0.0,1.0,1.0])
#         normal =  np.matrix([1.0,0.0,0.0,0.0])
#         axis =  np.matrix([0.0,1.0,0.0,0.0])
#         point = np.matrix([-1.0,0.0,1.0,1.0])
#         expected_point = np.matrix([0.0,0.0,2.0,1.0])
#         galvo_pos = MagicMock()
#         galvo_pos.return_value = math.pi / 4.0

#         mirror = Mirror(base_point, normal, axis, galvo_pos)

#         result = mirror.reflect(point, 1.0)

#         self.assertProjectiveCoordinatesEqual(expected_point,result)

# class GalvoTest(unittest.TestCase):
#     def test_galvo_pos(self):
#         galvo = Galvo()

#         self.assertAlmostEquals(-pi / 8.0 , galvo.pos(-1.0),6)
#         self.assertAlmostEquals( pi / 8.0 , galvo.pos(1.0) ,6)
#         self.assertAlmostEquals( 0.0      , galvo.pos(0.0) ,6)
#         self.assertAlmostEquals(-pi / 16.0, galvo.pos(-0.5),6)
#         self.assertAlmostEquals( pi / 16.0, galvo.pos( 0.5),6)

# class LaserTest(unittest.TestCase,TestHelp):
#     def test_get_real_point_with_aimed_down(self):
#         #Setup
#         expected_target_point1 = np.matrix([0.0,0.0,1.0,1.0])
#         expected_target_point2 = np.matrix([0.0,0.0,2.0,1.0])
#         position = np.matrix([0.0,0.0,10.0,1.0])
#         point_at = np.matrix([0.0,0.0,1.0,1.0])
#         laser = Laser(position, point_at)
        
#         #Assert
#         self.assertProjectiveCoordinatesEqual(expected_target_point1, laser.fire(1.0))
#         self.assertProjectiveCoordinatesEqual(expected_target_point2, laser.fire(2.0))

#     def test_get_real_point_aimed_somewhere(self):
#         #Setup
#         expected_target_point1 = np.matrix([1.0,3.0,1.0,1.0])
#         position = np.matrix([4.0,6.0,4.0,1.0])
#         point_at = np.matrix([3.0,5.0,3.0,1.0])
#         laser = Laser(position, point_at)
        
#         #Assert
#         self.assertProjectiveCoordinatesEqual(expected_target_point1, laser.fire(1.0))

#     def test_get_real_point_with_moved_laser(self):
#         #Setup
#         expected_target_point1 = np.matrix([1.0,3.0,1.0,1.0])
#         position = np.matrix([4.0,6.0,4.0,1.0])
#         point_at = np.matrix([3.0,5.0,3.0,1.0])
#         laser = Laser(position, point_at)
        
#         #Assert
#         self.assertProjectiveCoordinatesEqual(expected_target_point1, laser.fire(1.0))

#     def test_should_throw_exception_when_laser_axis_is_parallel_to_point_at(self):
#         #Setup
#         position = np.matrix([0.0,0.0,1.0,1.0])
#         point_at = np.matrix([1.0,0.0,1.0,1.0])
#         laser = Laser(position, point_at)
#         with self.assertRaises(Exception):
#             laser.fire(0.0)

class PeachyPrinterTest(unittest.TestCase,TestHelp):
    @patch('infrastructure.simulator.Laser')
    def test_write(self, mock_Laser):
        #Setup
        deflection1 = 1.0
        deflection2 = -1.0
        z_height = 10
        position = np.matrix([0.0,0.0,0.0,1.0])
        laser_point_at = np.matrix([1.0,0.0,0.0,1.0])

        phantom_laser1_position = np.matrix([1.0,0.0,7.0,1.0])
        phantom_laser1_point_at = np.matrix([1.0,1.0,0.0,1.0])

        phantom_laser2_position = np.matrix([2.0,0.0,0.0,1.0])
        phantom_laser2_point_at = np.matrix([1.0,2.0,0.0,1.0])
        
        laser = MagicMock()
        laser.position = position
        laser.point_at = laser_point_at

        mock_Laser.return_value.position = phantom_laser1_position
        mock_Laser.return_value.point_at = phantom_laser1_point_at
        mock_Laser.return_value.fire.return_value = [1.0,2.0,3.0,1.0]

        mirror1 = MagicMock()
        mirror1_values = [phantom_laser1_position, phantom_laser1_point_at ] 
        def mirror1_side_effect(a,b):
            return mirror1_values.pop(0)
        mirror1.reflect.side_effect = mirror1_side_effect

        mirror2 = MagicMock()
        mirror2_values = [phantom_laser2_position, phantom_laser2_point_at ] 
        def mirror2_side_effect(a,b):
            return mirror2_values.pop(0)
        mirror2.reflect.side_effect = mirror2_side_effect

        pp = PeachyPrinter(mirror1, mirror2, laser)

        #Execute
        pp.write(deflection1,deflection2, z_height)

        #Assert
        self.assertEquals((phantom_laser1_position, phantom_laser1_point_at), mock_Laser.mock_calls[0][1])
        self.assertEquals((phantom_laser2_position, phantom_laser2_point_at), mock_Laser.mock_calls[1][1])
        
        self.assertEquals((position, deflection1), mirror1.mock_calls[0][1])
        self.assertEquals((laser_point_at, deflection1), mirror1.mock_calls[1][1])
        
        self.assertEquals((phantom_laser1_position, deflection2), mirror2.mock_calls[0][1])
        self.assertEquals((phantom_laser1_point_at, deflection2), mirror2.mock_calls[1][1])
        
        mock_Laser.return_value.fire.assert_called_once_with(z_height)
        


if __name__ == '__main__':
    unittest.main()
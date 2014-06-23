import unittest
import numpy as np 
import math
import os
import sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.transformer2 import Laser, Mirror

class TestHelp(object):
    epsilon = 0.000001
    def assertProjectiveCoordinatesEqual(self, a,b):
        for i in range(3):
            diff = a[0,i]/a[0,3] - b[0,i]/b[0,3]
            self.assertTrue(abs(diff)<self.epsilon, 'Was out by : %s' % diff)

class MirrorTest(unittest.TestCase,TestHelp):
    def test_reflect_refects_at_origin_when_perpendicular_to_origin(self):
        base_point = np.matrix([0.0,0.0,0.0,1.0])
        point = np.matrix([0.0,0.0,2.0,1.0])
        expected_point = np.matrix([0.0,0.0,-2.0,1.0])
        normal =  np.matrix([0.0,0.0,1.0,0.0])
        mirror = Mirror(base_point, normal)

        result = mirror.reflect(point)

        self.assertProjectiveCoordinatesEqual(expected_point,result)

    def test_reflect_refects(self):
        base_point = np.matrix([0.0,0.0,0.0,1.0])
        point = np.matrix([1.0,0.0,3.0,1.0])
        expected_point = np.matrix([-3.0,0.0,-1.0,1.0])
        normal = np.matrix([math.sqrt(2)/2,0.0,math.sqrt(2)/2,0.0])

        mirror = Mirror(base_point, normal)
        
        result = mirror.reflect(point)

        self.assertProjectiveCoordinatesEqual(expected_point,result)

    def test_reflect_refects_not_at_origin_when_perpendicular_to_the_point(self):
        base_point = np.matrix([0.0,0.0,1.0,1.0])
        point = np.matrix([0.0,0.0,2.0,1.0])
        expected_point = np.matrix([0.0,0.0,-0.0,1.0])
        normal =  np.matrix([0.0,0.0,1.0,0.0])
        mirror = Mirror(base_point, normal)

        result = mirror.reflect(point)

        self.assertProjectiveCoordinatesEqual(expected_point,result)

    def test_reflect_refects_not_at_origin_when_not_perpendicular_to_the_point(self):
        base_point = np.matrix([0.0,0.0,1.0,1.0])
        point = np.matrix([0.0,10.0,2.0,1.0])
        expected_point = np.matrix([0.0,10.0,-0.0,1.0])
        normal =  np.matrix([0.0,0.0,1.0,0.0])
        mirror = Mirror(base_point, normal)

        result = mirror.reflect(point)

        self.assertProjectiveCoordinatesEqual(expected_point,result)

class LaserTest(unittest.TestCase,TestHelp):
    def test_get_real_point_with_aimed_down(self):
        #Setup
        expected_target_point1 = np.matrix([0.0,0.0,1.0,1.0])
        expected_target_point2 = np.matrix([0.0,0.0,2.0,1.0])
        laser_posisition = np.matrix([0.0,0.0,10.0,1.0])
        point_at = np.matrix([0.0,0.0,1.0,1.0])
        laser = Laser(laser_posisition, point_at)
        
        #Assert
        self.assertProjectiveCoordinatesEqual(expected_target_point1, laser.fire(1.0))
        self.assertProjectiveCoordinatesEqual(expected_target_point2, laser.fire(2.0))

    def test_get_real_point_aimed_somewhere(self):
        #Setup
        expected_target_point1 = np.matrix([1.0,3.0,1.0,1.0])
        laser_posisition = np.matrix([4.0,6.0,4.0,1.0])
        point_at = np.matrix([3.0,5.0,3.0,1.0])
        laser = Laser(laser_posisition, point_at)
        
        #Assert
        self.assertProjectiveCoordinatesEqual(expected_target_point1, laser.fire(1.0))

    def test_get_real_point_with_moved_laser(self):
        #Setup
        expected_target_point1 = np.matrix([1.0,3.0,1.0,1.0])
        laser_posisition = np.matrix([4.0,6.0,4.0,1.0])
        point_at = np.matrix([3.0,5.0,3.0,1.0])
        laser = Laser(laser_posisition, point_at)
        
        #Assert
        self.assertProjectiveCoordinatesEqual(expected_target_point1, laser.fire(1.0))

    def test_should_throw_exception_when_laser_axis_is_parallel_to_point_at(self):
        #Setup
        laser_posisition = np.matrix([0.0,0.0,1.0,1.0])
        point_at = np.matrix([1.0,0.0,1.0,1.0])
        laser = Laser(laser_posisition, point_at)
        with self.assertRaises(Exception):
            laser.fire(0.0)


if __name__ == '__main__':
    unittest.main()


import os
import sys
import numpy as np
import math
import logging

np.seterr(all='raise')

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from peachyprinter.domain.transformer import Transformer

class SquareTransform(object):
    def __init__(self,points):
        if len(points) != 4:
            raise Exception("Requires 4 deflection/actual pairs for setup")
        self.transformation_matrix = self._generate_transformation_matrix(points)

    def fit(self,x, y):
        actual_coordanates = np.array([[x], [y], [1]])
        deflections = self.transformation_matrix * actual_coordanates
        [kx, ky, k] = [ deflections.item(i, 0) for i in range(3) ]
        return [kx/k, ky/k]

    def _generate_transformation_matrix(self,points):
        base_matrix = self._build_forward_matrix(points)
        solutions_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        solved_matrix = np.linalg.solve(base_matrix,solutions_vector)
        forwards_matrix = np.matrix([solved_matrix[0:3], solved_matrix[3:6], solved_matrix[6:9]])
        return forwards_matrix.I

    def _build_forward_matrix(self, points):
        matrix = []
        index = 0
        for ((deflection_x,deflection_y),(actual_x,actual_y))in points:
            actuals = self._actuals(index, actual_x,actual_y)
            index += 1
            matrix.append([ deflection_x, deflection_y, 1,  0,  0,  0,  0,  0,  0] + actuals[0])
            matrix.append([ 0,  0,  0, deflection_x, deflection_y,  1,  0,  0,  0] + actuals[1])
            matrix.append([ 0,  0,  0,  0,  0,  0, deflection_x, deflection_y,  1] + actuals[2])
        matrix.append([ 1,  1,  1,  1,  1,  1,  1,  1,  1,     0,   0,   0,   0 ])
        return np.matrix(matrix)

    def _actuals(self,index,actual_x,actual_y):
        augment = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for column in range(0,4):
            if column == index:
                augment[0][column] = -actual_x
                augment[1][column] = -actual_y
                augment[2][column] = -1
        return augment

class PointTransformer(Transformer):
    def __init__(self, calibration_points):
        if len(calibration_points) < 12:
            logging.error("Not Enough Calibration Points")
            raise Exception("Not Enough Calibration Points")

        self.squarer = SquareTransform(calibration_points[:4])
        self.monomials = [
            lambda x,y : x**3,
            lambda x,y : x**2*y,
            lambda x,y : x*y**2,
            lambda x,y : y**3,
            lambda x,y : x**2,
            lambda x,y : x*y,
            lambda x,y : y**2,
            lambda x,y : x,
            lambda x,y : y,
            lambda x,y : 1
        ]

        self.calibrated_bend_x, self.calibrated_bend_y, self.coeffecient_vector_x, self.coeffecient_vector_y, self.calibrated_scale = self._get_best_bends(calibration_points,self.monomials)

    def _get_best_bends(self,points,monomials):
        best_bend = self._find_best_bends(
            points,
            monomials,
            range(1,2001, 500),
            range(1, 2001, 500),
            range(1, 2001, 500),
            500,
            (0, 0, 0 ,0, 0, 10.0)
            )
        logging.info("Best Bend: %s,%s: %s" % (best_bend[0],best_bend[1], best_bend[4]))
        return best_bend[:5]

    factor = 1000.0
    def _find_best_bends(self,points,monomials, scale_range, x_range, y_range, step, best_bend):
        for s in scale_range:
            for y in y_range:
                for x in x_range:
                    xbend = x / self.factor
                    ybend = y / self.factor
                    scale = s / self.factor
                    (coeffecient_vector_d1, error_d1), (coeffecient_vector_d2 , error_d2)= self._get_coeffecient_vectors(points, monomials,xbend,ybend,scale )
                    error = error_d1[0] + error_d2[0]
                    if best_bend[5] > error:
                        logging.info('New Best: %s %s : %s -> %s' % (xbend, ybend, scale, error ))
                        best_bend = (xbend, ybend, coeffecient_vector_d1,coeffecient_vector_d2, scale, error)
        new_step = int(step - math.ceil(step / 2.0))
        if new_step > 0:
            x_range = range(int(best_bend[0] * self.factor) - step, int(best_bend[0] * self.factor) + step, new_step)
            y_range = range(int(best_bend[1] * self.factor) - step, int(best_bend[1] * self.factor) + step, new_step)
            s_range = range(int(best_bend[4] * self.factor) - step, int(best_bend[4] * self.factor) + step, new_step)
            return self._find_best_bends(points,monomials,s_range,x_range,y_range,new_step, best_bend)
        else:
            return best_bend

    def _get_coeffecient_vectors(self, points, monomials,xbend,ybend,scale):
        target_deflection_1 = []
        target_deflection_2 = []
        rows = []
        for ((deflection_1,deflection_2),(actual_x,actual_y)) in points:
            target_deflection_1.append(deflection_1)
            target_deflection_2.append(deflection_2)
            fit_x, fit_y = self.squarer.fit(actual_x,actual_y)
            bend_x,bend_y = self._bend(fit_x, fit_y,xbend,ybend,scale)
            rows.append([ f(bend_x,bend_y) for f in monomials ])

        coeffecient_matrix = np.matrix(rows)
        target_vector_d1 = np.array(target_deflection_1)
        target_vector_d2 = np.array(target_deflection_2)

        results_d1 = np.linalg.lstsq(coeffecient_matrix, target_vector_d1)[:2]
        results_d2 = np.linalg.lstsq(coeffecient_matrix, target_vector_d2)[:2]
        return (results_d1, results_d2)

    def _bend(self,x,y,xbend,ybend,scale):
        bent_x = xbend * (scale * math.atan(x / scale)) + (1.0-xbend)  * x
        bent_y = ybend * (scale * math.atan(y / scale)) + (1.0-ybend)  * y
        return (bent_x, bent_y)

    def transform(self,xyz):
        x,y,z = xyz
        fit_x, fit_y = self.squarer.fit(x,y)
        bend_x,bend_y = self._bend(fit_x, fit_y,self.calibrated_bend_x,self.calibrated_bend_y, self.calibrated_scale)

        transform_x = sum( [ m * a(bend_x,bend_y) for (m,a) in zip(self.coeffecient_vector_x, self.monomials)] )
        transform_y = sum( [ m * a(bend_x,bend_y) for (m,a) in zip(self.coeffecient_vector_y, self.monomials)] )
        return [ transform_x,transform_y, z ]

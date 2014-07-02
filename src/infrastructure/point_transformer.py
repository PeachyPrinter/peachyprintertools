import os
import sys
import numpy as np
np.seterr(all='raise')

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from domain.transformer import Transformer

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
            raise Exception("Not Enough Points")

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

        self.coeffecients_x,self.coeffecients_y  = self._get_coeffecient_vectors(calibration_points, self.monomials)
        print('Cx: %s' % self.coeffecients_x)
        print('Cy: %s' % self.coeffecients_y)

    def _get_coeffecient_vectors(self, points, monomials):
        target_deflection_1 = []
        target_deflection_2 = []
        rows = []
        for ((deflection_1,deflection_2),(actual_x,actual_y)) in points:
            target_deflection_1.append(deflection_1)
            target_deflection_2.append(deflection_2)
            fit_x, fit_y = self.squarer.fit(actual_x,actual_y)
            # pin_x = self._x_de_pincushion(fit_xy[0],xbend)
            # pin_y = self._y_de_pincushion(fit_xy[1],ybend)
            # rows.append([ f(pin_x,pin_y) for f in monomial ])
            rows.append([ f(fit_x,fit_y) for f in monomials ])

        coeffecient_matrix = np.matrix(rows)
        target_vector_d1 = np.array(target_deflection_1)
        target_vector_d2 = np.array(target_deflection_2)

        results_d1 = np.linalg.lstsq(coeffecient_matrix, target_vector_d1)[:1]
        results_d2 = np.linalg.lstsq(coeffecient_matrix, target_vector_d2)[:1]
        return (results_d1, results_d2)

        return 

    def transform(self,xyz):
        x,y,z = xyz
        fit_x, fit_y = self.squarer.fit(x,y)
        transform_x = np.sum( [ m * a(fit_x,fit_y) for (m,a) in zip(self.coeffecients_x, self.monomials)] )
        transform_y = np.sum( [ m * a(fit_x,fit_y) for (m,a) in zip(self.coeffecients_y, self.monomials)] )
        return [ transform_x,transform_y, z ]

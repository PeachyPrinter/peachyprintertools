import cv2, cv
import time
import os

'''OpenCV web camera to file for testing purposes'''
class CameraControlSpike(object):

    def __init__(self,output_folder):
        self.output_folder = output_folder
        self.photoNumber = 0
        self.start = time.time()

    def take_a_photo(self,):
        vc = None
        try:
            vc = cv2.VideoCapture()
            vc.set(cv.CV_CAP_PROP_FRAME_WIDTH, 800.0)
            vc.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 600.0)
            vc.set(cv.CV_CAP_PROP_CONTRAST,50.0)
            # vc.set(cv.CV_CAP_PROP_EXPOSURE, )
            vc.set(cv.CV_CAP_PROP_BRIGHTNESS, -10.0)
            vc.open(0)
            if vc.isOpened():
                ret, frame = vc.read()
                if ret:
                    filename = str(self.start) + '-' + str(self.photoNumber) + '.jpg'
                    fle = os.path.join(self.output_folder, filename )
                    self.photoNumber += 1
                    cv2.imwrite(fle, frame)
                else:
                    print('Photo Failed')

        except Exception as ex:
            print(ex)

        finally:
            if vc.isOpened():
                vc.release()

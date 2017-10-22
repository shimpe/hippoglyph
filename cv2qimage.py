from PyQt5 import QtGui

class Cv2QImage(object):
    def __init__(self, cvimage):
        self.image = QtGui.QImage(cvimage, cvimage.shape[1], \
                             cvimage.shape[0], cvimage.shape[1] * 3, QtGui.QImage.Format_RGB888).rgbSwapped()


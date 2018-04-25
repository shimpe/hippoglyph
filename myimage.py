from PyQt5 import QtGui

from cv2qimage import Cv2QImage


class MyImage(object):
    def __init__(self, image):
        self.image = Cv2QImage(image).image
        self.pixmap = QtGui.QPixmap(self.image)
        self.item = None

    def add_to_scene(self, scene, minx, miny, maxx, maxy):
        assert (self.item is None)
        self.item = scene.addPixmap(self.pixmap)

    def remove_from_scene(self, scene):
        if self.item is not None:
            scene.removeItem(self.item)
            self.item = None

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QRadialGradient, QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem
from random import uniform, choice

from constants import FS


class Trigger(object):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.time = 0
        self.scale = 75
        self.color = color
        self.scene = None
        self.min_x = None
        self.min_y = None
        self.max_x = None
        self.max_y = None

        self.visited = True
        self.added = False

    def get_collision_info(self):
        return dict()

    def set_visited(self, val):
        self.visited = val

    def remove_from_scene(self):
        if self.scene is not None:
            self.scene.remove(self.circle)
            self.time = 0

    def add_to_scene(self, scene, min_x, min_y, max_x, max_y):
        self.scene = scene
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.add_to_scene_private(scene, min_x, min_y, max_x, max_y)
        self.added = True

    def update(self, udp_client, deltat, collisionInfo):
        self.update_private(udp_client, deltat, collisionInfo)

    def collidesWithItem(self, item):
        return self.collidesWithItem_private(item)

    def add_to_scene_private(self, scene, min_x, min_y, max_x, max_y):
        pass

    def update_private(self, udp_client, deltat):
        pass

    def collidesWithItem_private(self, item):
        return False

class GreenTrigger(Trigger):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.circle = None

    def add_to_scene_private(self, scene, min_x, min_y, max_x, max_y):
        if self.circle is None:
            self.circle = QGraphicsEllipseItem()
            self.scene.addItem(self.circle)
            self.time = 0
        self.circle.setRect(self.x, self.y, self.scale, self.scale)
        self.circle.setPen(QPen(Qt.NoPen))
        radgrad = QRadialGradient(self.x + self.scale / 2.0, self.y + self.scale, self.scale, self.x, self.y)
        radgrad.setColorAt(0, QColor(0, 255, 0, 255));
        radgrad.setColorAt(1, QColor(255, 255, 255, 0));
        self.circle.setBrush(QBrush(radgrad))

    def collidesWithItem_private(self, item):
        if self.circle.collidesWithItem(item):
            return True
        return False

    def update_private(self, udp_client, deltat, collisionInfo):
        if self.circle is not None:
            self.time = self.time + 0.3
            self.scale = self.scale + 5 * np.sin(2 * np.pi * 1 / FS * self.time / 250)
            self.add_to_scene(self.scene, self.min_x, self.min_y, self.max_x, self.max_y)

class RedTrigger(Trigger):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.circle = None

    def add_to_scene_private(self, scene, min_x, min_y, max_x, max_y):
        if self.circle is None:
            self.circle = QGraphicsEllipseItem()
            self.scene.addItem(self.circle)
            self.time = 0
        self.circle.setRect(self.x, self.y, self.scale, self.scale)
        self.circle.setPen(QPen(Qt.NoPen))
        radgrad = QRadialGradient(self.x + self.scale / 2.0, self.y + self.scale, self.scale, self.x, self.y)
        radgrad.setColorAt(0, QColor(255, 0, 0, 255));
        radgrad.setColorAt(1, QColor(255, 255, 255, 0));
        self.circle.setBrush(QBrush(radgrad))

    def get_collision_info(self):
        spread = 0.8
        return { 'multiply_speed' :  (1 - spread/2) + uniform(0, spread) }

    def collidesWithItem_private(self, item):
        if self.circle.collidesWithItem(item):
            return True
        return False

    def update_private(self, udp_client, deltat, collisionInfo):
        if self.circle is not None:
            self.time = self.time + 0.3
            self.scale = self.scale + 5 * np.sin(2 * np.pi * 1 / FS * self.time / 250)
            self.add_to_scene(self.scene, self.min_x, self.min_y, self.max_x, self.max_y)

class YellowTrigger(Trigger):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.circle = None

    def add_to_scene_private(self, scene, min_x, min_y, max_x, max_y):
        if self.circle is None:
            self.circle = QGraphicsEllipseItem()
            self.scene.addItem(self.circle)
            self.time = 0
        self.circle.setRect(self.x, self.y, self.scale, self.scale)
        self.circle.setPen(QPen(Qt.NoPen))
        radgrad = QRadialGradient(self.x + self.scale / 2.0, self.y + self.scale, self.scale, self.x, self.y)
        radgrad.setColorAt(0, QColor(255, 255, 0, 255));
        radgrad.setColorAt(1, QColor(255, 255, 255, 0));
        self.circle.setBrush(QBrush(radgrad))

    def get_collision_info(self):
        return { 'change_rays' : choice([-1, -2, 2, 1])}

    def collidesWithItem_private(self, item):
        if self.circle.collidesWithItem(item):
            return True
        return False

    def update_private(self, udp_client, deltat, collisionInfo):
        if self.circle is not None:
            self.time = self.time + 0.3
            self.scale = self.scale + 5 * np.sin(2 * np.pi * 1 / FS * self.time / 250)
            self.add_to_scene(self.scene, self.min_x, self.min_y, self.max_x, self.max_y)

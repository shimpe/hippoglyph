import random

import numpy as np
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsLineItem

from constants import THIN, THICK
from linecalc import LineCalc


class CrossPoint(object):
    def __init__(self, x, y, label, no_of_rays, color):
        self.x = x
        self.y = y
        self.rot = 0
        self.label = label
        self.color = color
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        self.scene = None
        self.text = None
        self.rays = no_of_rays
        self.lines = [None for i in range(self.rays)]
        self.thickness = THIN
        self.walk = False

    def remove_from_scene(self):
        if self.scene is not None:
            for l in self.lines:
                self.scene.remove_item(l)
            self.scene.remove_item(self.text)
            self.lines = [None for i in range(self.rays)]
            self.text = None

    def add_to_scene(self, scene, min_x, min_y, max_x, max_y):
        if None in self.lines:
            self.lines = [QGraphicsLineItem() for i in range(self.rays)]
            for l in self.lines:
                scene.addItem(l)
        if self.text is None:
            self.text = QGraphicsTextItem()
            scene.addItem(self.text)
        self.scene = scene
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        for i, l in enumerate(self.lines):
            points = LineCalc(self.x, self.y, np.deg2rad(self.rot) + np.deg2rad(i * 180 / self.rays)).endpoints(min_x,
                                                                                                                min_y,
                                                                                                                max_x,
                                                                                                                max_y)
            # print(points)
            if points:
                l.setLine(points[0][0], points[0][1], points[1][0], points[1][1])
                p = QPen(self.color, self.thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin);
                l.setPen(p)

        font = QFont("Arial", 75)
        self.text.setPos(QPointF(self.x, self.y))
        self.text.setPlainText(self.label)
        self.text.setDefaultTextColor(Qt.white)
        self.text.setFont(font)

    def update(self, deltat, collides=False):
        if None not in self.lines:
            self.rot = self.rot + deltat / 250.0
            if collides:
                self.thickness = THICK
            else:
                self.thickness = THIN
            if self.walk:
                target = 1
                beta = 1.0 / target
                X = random.expovariate(beta)
                Y = random.expovariate(beta)
                if random.choice([True, False]):
                    self.x += X
                else:
                    self.x -= X
                if random.choice([True, False]):
                    self.y += Y
                else:
                    self.y -= Y
            self.add_to_scene(self.scene, self.min_x, self.min_y, self.max_x, self.max_y)

    def collidesWithItem(self, item):
        for l in self.lines:
            if item.collidesWithItem(l):
                return True
        return False

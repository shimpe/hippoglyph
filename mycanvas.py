import pickle

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene

from constants import DELAY, INPUT_INTERVAL, CAMWIDTH, CAMHEIGHT
from extract import load_model, unwarp, find_letters, cutout_letters, cleanup_word, predict
from mymodel import MyModel
from ui_mainwindow import Ui_MainWindow


class MyCanvas(object):
    def __init__(self, camera):
        self.mainwin = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.mainwin)
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.camera_scene = QGraphicsScene()
        self.ui.cameraView.setScene(self.camera_scene)
        self.datamodel = MyModel()
        self.camera = camera
        self.liveinput_timer = None
        self.anim_timer = None

        self.bindir = "/home/shimpe/development/python/hippoglyph/EMNIST/bin"
        self.model = load_model(self.bindir)
        self.mapping = pickle.load(open('%s/mapping.p' % self.bindir, 'rb'))

    def display_model(self):
        self.scene.clear()
        self.datamodel.add_to_scene(self.scene, 0, 0, CAMWIDTH, CAMHEIGHT)
        self.datamodel.set_camera_image(self.camera_scene, self.camera.image)

    def show(self):
        self.mainwin.showMaximized()
        self.mainwin.show()
        self.ui.graphicsView.setSceneRect(0, 0, CAMWIDTH, CAMHEIGHT)
        self.ui.graphicsView.setBackgroundBrush(QColor(Qt.black))
        self.ui.cameraView.setSceneRect(0, 0, CAMWIDTH, CAMHEIGHT)
        self.ui.cameraView.setBackgroundBrush(QColor(Qt.black))
        self.update_liveinput()
        camBounds = self.camera_scene.itemsBoundingRect()
        camBounds.setWidth(camBounds.width() * 1.01)
        camBounds.setHeight(camBounds.height() * 1.01)
        self.ui.graphicsView.fitInView(camBounds, Qt.KeepAspectRatio)
        self.ui.cameraView.fitInView(camBounds, Qt.KeepAspectRatio)

    def add_crosspoint(self, x, y, label, rays, color):
        self.datamodel.add_crosspoint(x, y, label, rays, color)

    def add_trigger(self, x, y, color):
        self.datamodel.add_trigger(x, y, color)

    def update(self):
        self.datamodel.update(DELAY)
        camBounds = self.camera_scene.itemsBoundingRect()
        camBounds.setWidth(camBounds.width() * 1.01)
        camBounds.setHeight(camBounds.height() * 1.01)
        self.ui.graphicsView.fitInView(camBounds, Qt.KeepAspectRatio)

    def update_liveinput(self):
        ok, image = self.camera.take_input()
        if ok:
            unwarped_image = unwarp(image)
            if unwarped_image is not None:
                letters, letter_image = find_letters(unwarped_image)
                cut_letters = cutout_letters(unwarped_image, letters)
                import cv2
                cv2.imshow("letter_image", letter_image)
                self.datamodel.set_camera_image(self.camera_scene, image)
                self.words = []
                current_word = ""
                for l in cut_letters:
                    if l is None:
                        self.words.append(cleanup_word(current_word))
                        current_word = ""
                    else:
                        current_word += predict(self.model, self.mapping, l)
                if current_word:
                    self.words.append(cleanup_word(current_word))

        if self.liveinput_timer is not None:
            self.datamodel.update_time_left(INPUT_INTERVAL, self.liveinput_timer.remainingTime())
        camBounds = self.camera_scene.itemsBoundingRect()
        camBounds.setWidth(camBounds.width() * 1.01)
        camBounds.setHeight(camBounds.height() * 1.01)
        self.ui.cameraView.fitInView(camBounds, Qt.KeepAspectRatio)

    def start_animation_timer(self):
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update)
        self.anim_timer.start(DELAY)

    def start_liveinput_timer(self):
        self.liveinput_timer = QTimer()
        self.liveinput_timer.timeout.connect(self.update_liveinput)
        self.liveinput_timer.start(INPUT_INTERVAL)

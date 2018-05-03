import pickle
import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene

from constants import DELAY, INPUT_INTERVAL, CAMWIDTH, CAMHEIGHT, READ_INTERVAL
from extract import load_model, unwarp, cleanup_word, predict, \
    threshold_image, denoise_image, segment_letters, order_letters
from mymodel import MyModel
from mycontroller import MyController
from ui_mainwindow import Ui_MainWindow
from vectortween.Mapping import Mapping
from threading import RLock

class MyCanvas(object):
    def __init__(self, camera):
        self.mainwin = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.mainwin)
        self.camera_scene = QGraphicsScene()
        self.ui.cameraView.setScene(self.camera_scene)
        self.camera = camera
        self.liveinput_timer = None
        self.counter = 0
        self.words = []
        self.lock = RLock()
        self.cam_image_fit_needed = True
        self.datamodel = MyModel()
        self.controller = MyController(self.datamodel)
        self.bindir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "EMNIST", "bin")
        self.model = load_model(self.bindir)
        self.mapping = pickle.load(open('%s/mapping.p' % self.bindir, 'rb'))

    def display_model(self):
        self.datamodel.set_camera_image(self.camera_scene, self.camera.image)
        self.controller.send_updates()

    def show(self):
        self.mainwin.showMaximized()
        self.mainwin.show()
        self.ui.cameraView.setSceneRect(0, 0, CAMWIDTH, CAMHEIGHT)
        self.ui.cameraView.setBackgroundBrush(QColor(Qt.black))
        self.update_liveinput()
        camBounds = self.camera_scene.itemsBoundingRect()
        camBounds.setWidth(camBounds.width() * 1.01)
        camBounds.setHeight(camBounds.height() * 1.01)
        if self.cam_image_fit_needed:
            self.ui.cameraView.fitInView(camBounds, Qt.KeepAspectRatio)
            self.cam_image_fit_needed = False

    def update(self):
        with self.lock:
            camBounds = self.camera_scene.itemsBoundingRect()
            camBounds.setWidth(camBounds.width() * 1.01)
            camBounds.setHeight(camBounds.height() * 1.01)

    def update_liveinput(self):
        with self.lock:
            ok, image = self.camera.take_input()
            if ok:
                self.datamodel.set_camera_image(self.camera_scene, image)
            self.counter += 1
            if ok and (self.counter % READ_INTERVAL == 0):
                unwarped_image = self.image_to_words(image)
                mapped_words = []
                for i, w in enumerate(self.words):
                    imgw = unwarped_image.shape[1]
                    mapped_x = Mapping.linlin(w[1][0], 0, imgw, 0, 1023)
                    imgh = unwarped_image.shape[0]
                    mapped_y = Mapping.linlin(w[1][1], 0, imgh, 0, 599)
                    if w is not None:
                        mapped_words.append((w, mapped_x, mapped_y))
                self.datamodel.words = mapped_words
                self.display_model()

            camBounds = self.camera_scene.itemsBoundingRect()
            camBounds.setWidth(camBounds.width() * 1.01)
            camBounds.setHeight(camBounds.height() * 1.01)
            self.ui.cameraView.fitInView(camBounds, Qt.KeepAspectRatio)

    def image_to_words(self, image):
        self.counter = 0
        unwarped_image = unwarp(image)
        if unwarped_image is None:
            print("SKIP DETECTION")
        else:
            image = threshold_image(unwarped_image)
            image = denoise_image(image)
            all_letters = segment_letters(image)
            cut_letters = order_letters(all_letters)
            self.words = []
            current_word = ""
            avgX = 0
            avgY = 0
            wordLength = 0
            for l in cut_letters:
                if l is None:
                    avgX = avgX / wordLength if wordLength != 0 else 0
                    avgY = avgY / wordLength if wordLength != 0 else 0
                    self.words.append([cleanup_word(current_word), (avgX, avgY)])
                    current_word = ""
                    avgX = 0
                    avgY = 0
                    wordLength = 0
                else:
                    letter, pos = l
                    current_word += predict(self.model, self.mapping, letter)
                    avgX += pos[0]
                    avgY += pos[1]
                    wordLength += 1
            if current_word:
                avgX = avgX / wordLength if wordLength != 0 else 0
                avgY = avgY / wordLength if wordLength != 0 else 0
                self.words.append([cleanup_word(current_word), (avgX, avgY)])
        return unwarped_image

    def start_liveinput_timer(self):
        self.liveinput_timer = QTimer()
        self.liveinput_timer.timeout.connect(self.update_liveinput)
        self.liveinput_timer.start(INPUT_INTERVAL)

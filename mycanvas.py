import pickle

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene

from constants import DELAY, INPUT_INTERVAL, CAMWIDTH, CAMHEIGHT, READ_INTERVAL
from extract import load_model, unwarp, find_letters, cutout_letters, cleanup_word, predict, debug_display
from mymodel import MyModel
from colorgenerator import ColorGenerator
from ui_mainwindow import Ui_MainWindow
from vectortween.Mapping import Mapping
from pythonosc import udp_client
from threading import RLock


class MyCanvas(object):
    def __init__(self, camera):
        self.mainwin = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.mainwin)
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.camera_scene = QGraphicsScene()
        self.ui.cameraView.setScene(self.camera_scene)
        self.camera = camera
        self.liveinput_timer = None
        self.anim_timer = None
        self.counter = 0
        self.colorgenerator = ColorGenerator()
        self.words = []
        self.lock = RLock()
        try:
            self.udp_client = udp_client.SimpleUDPClient("127.0.0.1", 57120)
        except Exception as e:
            print("Exception occurred:\n{0}".format(e))
            self.udp_client = None
        self.datamodel = MyModel(self.udp_client)


        self.bindir = "/home/shimpe/development/python/hippoglyph/EMNIST/bin"
        self.model = load_model(self.bindir)
        self.mapping = pickle.load(open('%s/mapping.p' % self.bindir, 'rb'))

    def display_model(self):
        #self.scene.clear()
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

    def update_crosspoint(self, x, y, label, rays, color):
        self.datamodel.update_crosspoint(x, y, label, rays, color)

    def add_trigger(self, x, y, color):
        self.datamodel.add_trigger(x, y, color)

    def update_trigger(self, x, y, color):
        self.datamodel.update_trigger(x, y, color)

    def update(self):
        with self.lock:
            self.datamodel.update(DELAY)
            camBounds = self.camera_scene.itemsBoundingRect()
            camBounds.setWidth(camBounds.width() * 1.01)
            camBounds.setHeight(camBounds.height() * 1.01)
            self.ui.graphicsView.fitInView(camBounds, Qt.KeepAspectRatio)

    def update_liveinput(self):
        with self.lock:
            ok, image = self.camera.take_input()
            if ok:
                self.datamodel.set_camera_image(self.camera_scene, image)
            self.counter += 1
            if ok and (self.counter % READ_INTERVAL == 0):
                unwarped_image = self.image_to_words(image)

                no_of_col = len(self.words)
                colors = self.colorgenerator.get_colors(no_of_col)
                self.datamodel.prepare_update()
                for i, w in enumerate(self.words):
                    imgw = unwarped_image.shape[1]
                    mapped_x = Mapping.linlin(w[1][0], 0, imgw, 0, CAMWIDTH)
                    imgh = unwarped_image.shape[0]
                    mapped_y = Mapping.linlin(w[1][1], 0, imgh, 0, CAMHEIGHT)
                    if w is not None:
                        if w[0] == "t":
                            self.update_trigger(mapped_x, mapped_y, colors[i])
                        else:
                            print("{0}".format(w))
                            self.update_crosspoint(mapped_x, mapped_y, w[0], 2, colors[i])
                #self.datamodel.finish_update()
                self.display_model()

            if self.liveinput_timer is not None:
                self.datamodel.update_time_left(INPUT_INTERVAL, self.liveinput_timer.remainingTime())
            camBounds = self.camera_scene.itemsBoundingRect()
            camBounds.setWidth(camBounds.width() * 1.01)
            camBounds.setHeight(camBounds.height() * 1.01)
            self.ui.cameraView.fitInView(camBounds, Qt.KeepAspectRatio)

    def image_to_words(self, image):
        self.counter = 0
        unwarped_image = unwarp(image)
        if unwarped_image is None:
            print("SKIP DETECTION")
        elif unwarped_image is not None:
            # import cv2
            # cv2.imshow("unwarped image", unwarped_image)
            letters, letter_image = find_letters(unwarped_image)
            cut_letters = cutout_letters(unwarped_image, letters)
            # import cv2
            # cv2.imshow("letter_image", letter_image)
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

    def start_animation_timer(self):
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update)
        self.anim_timer.start(DELAY)

    def start_liveinput_timer(self):
        self.liveinput_timer = QTimer()
        self.liveinput_timer.timeout.connect(self.update_liveinput)
        self.liveinput_timer.start(INPUT_INTERVAL)

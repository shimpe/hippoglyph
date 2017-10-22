import cv2
import contextlib

@contextlib.contextmanager
def CameraResource(camId):
    class MyCamera(object):
        def __init__(self, camId):
            self.camId = camId
            self.sizeX = None
            self.sizeY = None
            self.image = None
            self.error = None
            self.capture = cv2.VideoCapture(self.camId)

        def set_image_size(self, sizeX, sizeY):
            # ziggi hd plus supports:
            # 3264x2448, 3264x1836, 2592x1944, 2048x1536, 1920x1080, 1600x1200, 1280x720, 1024x768, 800x600, 640x480
            self.sizeX = sizeX
            self.sizeY = sizeY
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.sizeX)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.sizeY)

        def take_input(self):
            self.error, self.image = self.capture.read()
            return self.error, self.image

        def release(self):
            cv2.VideoCapture(self.camId).release()

    camera = MyCamera(camId)
    yield camera
    print("FINI!")
    camera.release()


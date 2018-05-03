import contextlib
import cv2
import os


@contextlib.contextmanager
def CameraResource(no_of_cameras, camId, save_diagnostics=True, load_diagnostics=False):
    class MyCamera(object):
        def __init__(self, no_of_cameras, camId, save_diagnostics=save_diagnostics, load_diagnostics=load_diagnostics):
            self.no_of_cameras = no_of_cameras
            self.camId = camId
            self.sizeX = None
            self.sizeY = None
            self.image = None
            self.error = None
            if not load_diagnostics:
                self.capture = cv2.VideoCapture(self.no_of_cameras)
            else:
                self.capture = None
            self.save_diagnostics = save_diagnostics
            self.load_diagnostics = load_diagnostics
            self.save_diagnostics_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "diagnostics")

        def set_image_size(self, sizeX, sizeY):
            # ziggi hd plus supports:
            # 3264x2448, 3264x1836, 2592x1944, 2048x1536, 1920x1080, 1600x1200, 1280x720, 1024x768, 800x600, 640x480
            self.sizeX = sizeX
            self.sizeY = sizeY
            if self.capture is not None:
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.sizeX)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.sizeY)

        def take_input(self):
            if not self.load_diagnostics and self.capture is not None:
                self.error, self.image = self.capture.read()
            else:
                self.error, self.image = 1, cv2.imread(os.path.join(self.save_diagnostics_path, "diagnostic_image.jpg"))

            if self.save_diagnostics:
                cv2.imwrite(os.path.join(self.save_diagnostics_path, "diagnostic_image.jpg"), self.image)

            return self.error, self.image

        def release(self):
            if self.capture is not None:
                cv2.VideoCapture(self.camId).release()

    camera = MyCamera(no_of_cameras, camId)
    yield camera
    print("FINI!")
    camera.release()

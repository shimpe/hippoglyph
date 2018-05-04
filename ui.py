import sys
from PyQt5.QtWidgets import QApplication

from constants import CAMWIDTH, CAMHEIGHT
from mycamera import CameraResource
from mycanvas import MyCanvas

CAMID = 0      #1
NO_OF_CAM = 0  #2

def main():
    app = QApplication(sys.argv)
    with CameraResource(NO_OF_CAM, CAMID, load_diagnostics=False, save_diagnostics=True) as camera:
        camera.set_image_size(CAMWIDTH, CAMHEIGHT)
        canvas = MyCanvas(camera)
        canvas.show()
        canvas.display_model()
        canvas.start_liveinput_timer()

        sys.exit(app.exec_())


if __name__ == "__main__":
    main()

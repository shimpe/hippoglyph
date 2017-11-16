import sys
from PyQt5.QtWidgets import QApplication

from constants import CAMWIDTH, CAMHEIGHT
from mycamera import CameraResource
from mycanvas import MyCanvas

def main():
    app = QApplication(sys.argv)
    with CameraResource(1, load_diagnostics=True, save_diagnostics=False) as camera:
        camera.set_image_size(CAMWIDTH, CAMHEIGHT)
        canvas = MyCanvas(camera)
        canvas.show()
        canvas.display_model()
        canvas.start_animation_timer()
        canvas.start_liveinput_timer()

        sys.exit(app.exec_())


if __name__ == "__main__":
    main()

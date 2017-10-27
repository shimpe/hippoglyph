import random
import sys

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from constants import CAMWIDTH, CAMHEIGHT
from mycamera import CameraResource
from mycanvas import MyCanvas


def main():
    app = QApplication(sys.argv)
    with CameraResource(1) as camera:
        camera.set_image_size(CAMWIDTH, CAMHEIGHT)
        canvas = MyCanvas(camera)
        canvas.show()
        # cs = [(CAMWIDTH / 2.0, CAMHEIGHT / 3.0),
        #       (CAMWIDTH / 3.0, CAMHEIGHT / 2.0),
        #       (CAMWIDTH / 4.0, 4 * CAMHEIGHT / 5.0),
        #       (5 * CAMWIDTH / 6.0, CAMHEIGHT / 2.0),
        #       (3 * CAMWIDTH / 4.0, 5 * CAMHEIGHT / 7.0)]
        # ts = [(CAMWIDTH / 3.0, CAMHEIGHT / 4.0)]
        # golden_ratio_conjugate = 0.618033988749895
        #
        # h = random.uniform(0, 127)  # use random start value
        # for i, c in enumerate(cs):
        #     h = h + golden_ratio_conjugate
        #     h = h % 1
        #     color = QColor.fromHsv(h * 255, 0.5 * 255, 0.95 * 255, 160)
        #     canvas.add_crosspoint(c[0], c[1], "hello", 3, color)
        #
        # h = random.uniform(0, 127)
        # for i, t in enumerate(ts):
        #     h = h + golden_ratio_conjugate
        #     h = h % 1
        #     color = QColor.fromHsv(h * 255, 0.5 * 255, 0.95 * 255, 160)
        #     canvas.add_trigger(t[0], t[1], QColor.fromHsv(h * 255, 0.5 * 255, 0.95 * 255, 200))
        canvas.display_model()
        canvas.start_animation_timer()
        canvas.start_liveinput_timer()

        sys.exit(app.exec_())


if __name__ == "__main__":
    main()

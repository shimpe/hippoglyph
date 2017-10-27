from PyQt5.QtGui import QColor
import random

class ColorGenerator(object):
    def __init__(self):
        self.golden_ratio_conjugate = 0.618033988749895

    def get_colors(self, no_of_col):
        h = random.uniform(0, 127)  # use random start value
        colors = []
        for i in range(no_of_col):
            h = h + self.golden_ratio_conjugate
            h = h % 1
            colors.append(QColor.fromHsv(h * 255, 0.5 * 255, 0.95 * 255, 160))

        return colors
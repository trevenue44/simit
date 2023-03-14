from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPalette, QColor


class Canvas(QWidget):
    def __init__(self, parent):
        super(Canvas, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.move(0, 0)
        self.resize(200, 600)
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 100, 0))
        self.setPalette(palette)

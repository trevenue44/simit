from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPalette, QColor


class LeftColumn(QWidget):
    def __init__(self, parent=None):
        super(LeftColumn, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.move(0, 0)
        self.resize(200, 600)
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(100, 0, 0))
        self.setPalette(palette)

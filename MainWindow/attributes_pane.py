from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class AttributesPane(QWidget):
    def __init__(self, parent=None):
        super(AttributesPane, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.move(0, 0)
        self.resize(200, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgb(0, 0, 100);")


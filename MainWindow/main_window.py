from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from .left_column import LeftColumn
from .canvas import Canvas
from .right_column import RightColumn


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SIMIT")
        self.resize(800, 600)

        self.left_column = LeftColumn(self)
        self.canvas = Canvas(self)
        self.right_column = RightColumn(self)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.left_column, 1)
        self.layout.addWidget(self.canvas, 4)
        self.layout.addWidget(self.right_column, 1)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)


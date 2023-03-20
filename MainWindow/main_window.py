from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from .component_pane import ComponentPane
from .canvas import Canvas
from .attributes_pane import AttributesPane


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SIMIT")
        self.resize(800, 600)

        self.left_column = ComponentPane(self)
        self.canvas = Canvas(self)
        self.right_column = AttributesPane(self)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.layout.addWidget(self.left_column, 1)
        self.layout.addWidget(self.canvas, 4)
        self.layout.addWidget(self.right_column, 1)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)


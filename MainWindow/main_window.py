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

        self.component_pane = ComponentPane(self)
        self.canvas = Canvas(self)
        self.attributes_pane = AttributesPane(self)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.layout.addWidget(self.component_pane, 1)
        self.layout.addWidget(self.canvas, 4)
        self.layout.addWidget(self.attributes_pane, 1)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

        # connecting all necessary signals
        self.connect_signals()

    def connect_signals(self):
        # connecting a signal from the component pane to the canvas
        self.component_pane.component_selected.connect(self.component_selected_handler)

    def component_selected_handler(self, component):
        self.canvas.add_component(component)

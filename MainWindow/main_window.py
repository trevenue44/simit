from typing import Type

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QToolBar
from PyQt6.QtGui import QAction

from components.general import GeneralComponent

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

        self.componentPane = ComponentPane(self)
        self.canvas = Canvas(self)
        self.attributesPane = AttributesPane(self)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.layout.addWidget(self.componentPane, 1)
        self.layout.addWidget(self.canvas, 4)
        self.layout.addWidget(self.attributesPane, 1)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

        # create toolbar
        self._createToolBar()

        # connecting all necessary signals
        self._connectSignals()

    def _createToolBar(self):
        # creating a toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # adding actions to the toolbar
        button_action = QAction("Wire", self)
        button_action.setStatusTip("Wire")
        button_action.triggered.connect(self._onWireToolClick)
        button_action.setCheckable(True)

        toolbar.addAction(button_action)

    def _onWireToolClick(self, state: bool):
        self.canvas.onWireToolClick(state)

    def _connectSignals(self):
        # connecting a signal from the component pane to the canvas
        self.componentPane.signals.componentSelected.connect(self.onComponentSelect)

    def onComponentSelect(self, component: Type["GeneralComponent"]):
        self.canvas.addComponent(component)

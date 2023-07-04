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
        self.resize(1000, 800)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)

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
        wire_tool = QAction("Wire", self)
        wire_tool.setStatusTip("Wire")
        wire_tool.triggered.connect(self._onWireToolClick)
        wire_tool.setCheckable(True)
        toolbar.addAction(wire_tool)

        # add simulate action
        simulate_button = QAction("Simulate", self)
        simulate_button.setStatusTip("Simulate circuit on canvas")
        simulate_button.triggered.connect(self._onSimulateButtonClick)
        toolbar.addAction(simulate_button)

    def _onSimulateButtonClick(self):
        self.canvas.onSimulateButtonClick()

    def _onWireToolClick(self, state: bool):
        self.canvas.onWireToolClick(state)

    def _connectSignals(self):
        # connecting a signal from the component pane to the canvas
        self.componentPane.signals.componentSelected.connect(self.onComponentSelect)

        # pass selected instance component to the attributes pane
        self.canvas.signals.componentSelected.connect(self.onCanvasComponentSelect)

    def onComponentSelect(self, component: Type["GeneralComponent"]):
        self.canvas.addComponent(component)

    def onCanvasComponentSelect(self, component: GeneralComponent):
        self.attributesPane.onCanvasComponentSelect(component)

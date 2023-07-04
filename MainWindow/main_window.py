from typing import Type

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QToolBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize

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
        toolbar.setIconSize(QSize(28, 28))
        self.addToolBar(toolbar)

        # add simulate action
        simulate_button = QAction(QIcon("./assets/simulate-icon.png"), "Simulate", self)
        simulate_button.setStatusTip("Simulate circuit on canvas")
        simulate_button.triggered.connect(self._onSimulateButtonClick)
        toolbar.addAction(simulate_button)

        # adding actions to the toolbar
        wire_tool = QAction(QIcon("./assets/wire-tool-icon.png"), "Wire", self)
        wire_tool.setStatusTip("Wire")
        wire_tool.triggered.connect(self._onWireToolClick)
        wire_tool.setCheckable(True)
        toolbar.addAction(wire_tool)

        # adding actions to the toolbar
        toolbar.addSeparator()
        deleteSelectedComponentsButton = QAction(
            QIcon("./assets/bin-icon.png"), "Delete Selected Components", self
        )
        deleteSelectedComponentsButton.setStatusTip("Wire")
        deleteSelectedComponentsButton.triggered.connect(
            self.onDeleteSelectedComponentsClick
        )
        toolbar.addAction(deleteSelectedComponentsButton)

    def _onSimulateButtonClick(self):
        self.canvas.onSimulateButtonClick()

    def _onWireToolClick(self, state: bool):
        self.canvas.onWireToolClick(state)

    def _connectSignals(self):
        # connecting a signal from the component pane to the canvas
        self.componentPane.signals.componentSelected.connect(self.onComponentSelect)

        # pass selected instance component to the attributes pane
        self.canvas.signals.componentSelected.connect(self.onCanvasComponentSelect)

        # selected component on attributes pane is deleted
        self.attributesPane.signals.deleteComponent.connect(self.onDeleteComponent)

    def onComponentSelect(self, component: Type["GeneralComponent"]):
        self.canvas.addComponent(component)

    def onCanvasComponentSelect(self, component: GeneralComponent):
        self.attributesPane.onCanvasComponentSelect(component)

    def onDeleteComponent(self, uniqueID: str):
        self.canvas.deleteComponents(componentIDs=[uniqueID])

    def onDeleteSelectedComponentsClick(self):
        selectedComponentsIDs = self.canvas.selectedComponentsIDs
        if len(selectedComponentsIDs):
            button = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete selected components?",
                buttons=QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.Cancel,
            )
            if button == QMessageBox.StandardButton.Yes:
                self.canvas.deleteComponents(componentIDs=selectedComponentsIDs)

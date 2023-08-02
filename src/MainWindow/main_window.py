from typing import Type

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QToolBar,
    QMessageBox,
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize

from components.general import GeneralComponent

from .components_pane import ComponentsPane
from .canvas import Canvas
from .attributes_pane import AttributesPane
from .log_console import LogConsole

from logger import qt_log_handler


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("simit")
        self.resize(1000, 800)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)

        self.componentPane = ComponentsPane(self)
        self.canvas = Canvas(self)

        self.attributes_pane_and_log_console = QVBoxLayout()

        self.attributesPane = AttributesPane(self)
        self.log_console = LogConsole(self)

        self.attributes_pane_and_log_console.addWidget(self.attributesPane, 3)
        self.attributes_pane_and_log_console.addWidget(self.log_console, 1)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.layout.addWidget(self.componentPane, 1)
        self.layout.addWidget(self.canvas, 4)
        # self.layout.addWidget(self.attributesPane, 1)
        self.layout.addLayout(self.attributes_pane_and_log_console, 1)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

        # create toolbar
        self._createToolBar()

        # connecting all necessary signals
        self._connectSignals()

    def _createToolBar(self):
        """Create a toolbar for the main window"""
        # creating a toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(self.toolbar)

        self._create_and_add_simulate_action()
        self._create_and_add_wire_tool_action()
        self._create_and_add_rotate_action()

        # adding delete button to the toolbar
        self.toolbar.addSeparator()
        self._create_and_add_delete_action()

    def _create_and_add_simulate_action(self):
        """Create a simulate action and add it to the toolbar"""
        # add simulate action
        simulate_button = QAction(
            QIcon("src/assets/simulate-icon.png"), "Simulate", self
        )
        simulate_button.setStatusTip("Simulate circuit on canvas")
        simulate_button.triggered.connect(self._onSimulateButtonClick)
        self.toolbar.addAction(simulate_button)

    def _create_and_add_wire_tool_action(self):
        """Create a wire tool action and add it to the toolbar"""
        # adding wire tool action to the toolbar
        wire_tool = QAction(QIcon("src/assets/wire-tool-icon.png"), "Wire", self)
        wire_tool.setStatusTip("Wire")
        wire_tool.triggered.connect(self._onWireToolClick)
        wire_tool.setCheckable(True)
        self.toolbar.addAction(wire_tool)

    def _create_and_add_rotate_action(self):
        """Create a rotate action and add it to the toolbar"""
        # add rotate action to toolbar
        rotate_action = QAction(QIcon("src/assets/rotate-icon.png"), "Rotate", self)
        rotate_action.triggered.connect(self.rotateSelectedComponent)
        self.toolbar.addAction(rotate_action)

    def _create_and_add_delete_action(self):
        """Create a delete action and add it to the toolbar"""
        deleteSelectedComponentsButton = QAction(
            QIcon("src/assets/bin-icon.png"), "Delete", self
        )
        deleteSelectedComponentsButton.triggered.connect(
            self.onDeleteSelectedComponentsClick
        )
        self.toolbar.addAction(deleteSelectedComponentsButton)

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

        # connected log signal to log console
        qt_log_handler.signals.log.connect(self.log_console.on_log)

    def onComponentSelect(self, component: Type["GeneralComponent"]):
        """Slot to handle the componentSelected signal from the component pane"""
        self.canvas.addComponent(component)

    def onCanvasComponentSelect(self, component: GeneralComponent):
        """Slot to handle the componentSelected signal from the canvas"""
        self.attributesPane.onCanvasComponentSelect(component)

    def onDeleteComponent(self, uniqueID: str):
        """Slot to handle the deleteComponent signal from the attributes pane"""
        self.canvas.deleteComponents(componentIDs=[uniqueID])

    def onDeleteSelectedComponentsClick(self):
        """Slot to handle the deleteSelectedComponents signal from the toolbar"""
        selectedComponentsIDs = self.canvas.selectedComponentsIDs.copy()
        selectedWireIDs = self.canvas.selectedWireIDs.copy()
        if len(selectedComponentsIDs) or len(selectedWireIDs):
            messageText = "Are you sure you want to delete selected components?"
            if len(selectedWireIDs):
                messageText += "\n\nDeleting a Wire will delete the whole node."
            button = QMessageBox.question(
                self,
                "Confirm Delete",
                messageText,
                buttons=QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.Cancel,
            )
            if button == QMessageBox.StandardButton.Yes:
                self.canvas.deleteComponents(componentIDs=selectedComponentsIDs)
                self.canvas.deleteWires(wireIDs=selectedWireIDs)

    def rotateSelectedComponent(self):
        self.canvas.rotateSelectedComponents()

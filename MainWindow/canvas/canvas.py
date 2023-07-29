from typing import Type, Dict, List, Tuple
from PyQt6 import QtGui

from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPointF

from .grid_scene import GridScene
from components.general import GeneralComponent
from components.general.component_and_terminal_index import ComponentAndTerminalIndex
from components.wire_new import Wire

from SimulationBackend.middleware import CircuitNode
from SimulationBackend.circuit_simulator import CircuitSimulator

import constants


class Canvas(QGraphicsView):
    class Signals(QObject):
        componentSelected = pyqtSignal(GeneralComponent)

    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        # keep track of the state of the wire tool
        self.wireToolActive = False
        # keeping track of the terminals clicked when the wire tools is active.
        # format: list of tuples. Each tuple is supposed to be (componentID, terminalIndex)
        self.clickedTerminals: List[Tuple[str, int]] = []
        # keep track of the current wire the user is drawing
        self.currentWire: Wire | None = None

        self.components: Dict[str, GeneralComponent] = {}
        self.wires: Dict[str, Wire] = {}

        self.selectedComponentsIDs: List[str] = []

        # dictionary to store circuit nodes based on their uniqueIDs
        self.circuitNodes: Dict[str, CircuitNode] = {}

        # signals
        self.signals = self.Signals()

        self.initUI()

    def initUI(self):
        """
        Function to set the scene and some initial flags of the GraphicsView for optimization and behaviour
        """

        self.setScene(GridScene(self))
        # self.setBackgroundBrush(Qt.GlobalColor.black)

        self.setOptimizationFlag(
            QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True
        )
        # RubberBandDrag mode allows the selection of multiple components by dragging to draw a rectangle around them
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    def addComponent(self, component: Type["GeneralComponent"]) -> None:
        comp = component(compCount=len(self.components))
        try:
            comp.signals.terminalClicked.connect(self.onTerminalClick)
            comp.signals.componentSelected.connect(self.onComponentSelected)
            comp.signals.componentDeselected.connect(self.onComponentDeselected)
        except Exception as e:
            print(f"[INFO] Some component signals not connected - Error: {e}")
        self.scene().addItem(comp)
        self.components[comp.uniqueID] = comp

    def deleteComponents(self, componentIDs: List[str]):
        for componentID in componentIDs:
            component = self.components.get(componentID)
            if component is not None:
                self.scene().removeItem(component)
                del self.components[componentID]
                component.setSelected(False)

    def rotateSelectedComponents(self):
        for componentID in self.selectedComponentsIDs:
            component = self.components.get(componentID)
            component.rotate()

    def onComponentSelected(self, uniqueID: str):
        self.selectedComponentsIDs.append(uniqueID)
        # emit the component selected signal with the component instance
        self.signals.componentSelected.emit(self.components.get(uniqueID))

    def onComponentDeselected(self, uniqueID: str):
        self.selectedComponentsIDs.remove(uniqueID)

    def onWireToolClick(self, wireToolState: bool):
        self.wireToolActive = wireToolState
        # stop any current wire being drawn when the wire tool is off
        if not self.wireToolActive:
            # if there's a current wire on the scene, remove it
            if self.currentWire and self.currentWire in self.scene().items():
                self.scene().removeItem(self.currentWire)
            # stop drawing any current wire
            self.currentWire = None
            self.scene().update()

    def onTerminalClick(self, uniqueID: str, terminalIndex: int):
        if self.wireToolActive:
            # do anything related to wire if only the wire tool is active.
            # create a current wire if there is no current wire and no initial terminal has been clicked
            # create a new wire component and set that as the current wire component
            # start position of that wire will be the clicked terminal
            component = self.components.get(uniqueID)
            if self.currentWire is None and len(self.clickedTerminals) == 0:
                # get the start position from the component specified
                self.currentWire = Wire(
                    start=ComponentAndTerminalIndex(component, terminalIndex),
                    wireCount=len(self.wires),
                )
                self.clickedTerminals.append((uniqueID, terminalIndex))
            elif self.currentWire is not None and len(self.clickedTerminals) == 1:
                # making sure same terminal is not clicked twice when drawing a wire
                terminal = (uniqueID, terminalIndex)
                if terminal not in self.clickedTerminals:
                    # a second terminal has been clicked
                    # the end position of the wire has been clicked
                    # set the end poisiton
                    # stop drawing wire and set the nodes
                    self.currentWire.setEnd(
                        end=ComponentAndTerminalIndex(component, terminalIndex)
                    )
                    self.currentWire = None
                    self.clickedTerminals.append(terminal)
                    # update nodes when connection is done
                    ...
                    # clear the content of the clicked terminals list
                    self.clickedTerminals.clear()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.wireToolActive:
            # only do anything related to wire if the wire tool is active.
            # if there's a current wire alredy create update the points based on what point is clicked by the user
            if self.currentWire is not None:
                # get the point clicked by the user and normalis it to grid
                clickedPoint = self.normalizePointToGrid(self.mapToScene(event.pos()))
                # add the clicked point to the wire to handle the drawing of the wire.
                self.currentWire.addNewPoint(clickedPoint)
                # update the wire component on the scene to make the current wire show
                if self.currentWire in self.scene().items():
                    self.scene().removeItem(self.currentWire)
                    self.scene().addItem(self.currentWire)
                else:
                    self.scene().addItem(self.currentWire)
                self.scene().update()

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.scene().update()

    def normalizePointToGrid(self, p: QPointF) -> QPointF:
        x = round(p.x() / constants.GRID_SIZE) * constants.GRID_SIZE
        y = round(p.y() / constants.GRID_SIZE) * constants.GRID_SIZE
        return QPointF(x, y)

    def onSimulateButtonClick(self):
        print("simulating...")

        # create a circuit simulator instance with current data
        circuitSimulator = CircuitSimulator(
            components=self.components, circuitNodes=self.circuitNodes
        )

        # simulate the circuit
        results = circuitSimulator.simulate()

        if results is None:
            # if simulation fails and there is no results
            return

        # set the simulated node voltages
        self.setSimulatedNodeVoltages(results=results)
        # set simulation results for components
        self.setComponentsSimulationResults(results)

    def setSimulatedNodeVoltages(self, results: Dict[str, Dict[str, List[str]]]):
        voltages = results.get("voltages")
        for nodeID in self.circuitNodes.keys():
            nodeData = voltages.get(nodeID.lower())
            # add node data to the node
            self.circuitNodes.get(nodeID).setNodeData("V", nodeData)

    def setComponentsSimulationResults(self, results: Dict[str, Dict[str, List[str]]]):
        currents = results.get("currents")
        components = self.components

        for componentID in components.keys():
            for currentKey in currents.keys():
                if componentID.lower() in currentKey:
                    # the current is for that component
                    # set the current of that component to the simulation current
                    components.get(componentID).setSimulationResults(
                        "I", currents.get(currentKey)
                    )
                    break

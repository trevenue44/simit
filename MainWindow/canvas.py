from typing import Type, Dict, List, Tuple

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from components.general import GeneralComponent
from components.wire import Wire, ComponentAndTerminalIndex
from SimulationBackend.middleware import CircuitNode
from SimulationBackend.circuit_simulator import CircuitSimulator


class Canvas(QGraphicsView):
    class Signals(QObject):
        componentSelected = pyqtSignal(GeneralComponent)

    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.wireToolActive = False
        self.selectedTerminals = []

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
        self.setOptimizationFlag(
            QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True
        )
        # RubberBandDrag mode allows the selection of multiple components by dragging to draw a rectangle around them
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(Qt.GlobalColor.black)

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
        if not self.wireToolActive:
            self.selectedTerminals = []

    def onTerminalClick(self, uniqueID: str, terminalIndex: int):
        if self.wireToolActive:
            clickedTerminal = (uniqueID, terminalIndex)
            if clickedTerminal in self.selectedTerminals:
                # terminal already selected
                return
            self.selectedTerminals.append(clickedTerminal)

            if len(self.selectedTerminals) == 2:
                self.drawWire()
                self.selectedTerminals = []

    def drawWire(self):
        start = ComponentAndTerminalIndex(
            self.components.get(self.selectedTerminals[0][0]),
            self.selectedTerminals[0][1],
        )
        end = ComponentAndTerminalIndex(
            self.components.get(self.selectedTerminals[1][0]),
            self.selectedTerminals[1][1],
        )
        wire = Wire(start, end, wireCount=len(self.wires))
        # add new connection to existing nodes or create new nodes
        node = self.updateCircuitNodes()
        # add node to wire component to keep track of the data and changes
        wire.setCircuitNode(node)
        # add wire to scene
        self.scene().addItem(wire)
        # keep track of wire
        self.wires[wire.uniqueID] = wire

    def updateCircuitNodes(self):
        if len(self.circuitNodes) == 0:
            # there are no existing nodes
            # create a new node
            node = self.createNewCircuitNode(
                nodeCount=len(self.circuitNodes),
                componentTerminals=self.selectedTerminals,
            )
            return node

        # keep track of the newTerminals that are already node(s)
        terminalIntersections: set = set()
        # keep track of the nodes the new terminals intersect with
        nodesIntersectedWith: set = set()

        # if there are already circuitNodes
        # loops through the circuit nodes
        for nodeID in self.circuitNodes.keys():
            circuitNode = self.circuitNodes.get(nodeID)
            # compare the terminals involved in each node to the terminals involved in the new conection
            newTerminals = set(self.selectedTerminals)
            oldTerminals = set(circuitNode.componentTerminals)

            intersections = newTerminals.intersection(oldTerminals)

            if len(intersections) == 0:
                # means that new terminasl don't intersect with the node
                continue
            elif len(intersections) == 1:
                # only one of the new terminals intersect with current node
                # update the sets outside the loop that keep track of the terminals and nodes intersected with
                terminalIntersections.add(next(iter(intersections)))
                nodesIntersectedWith.add(nodeID)
            elif len(intersections) == 2:
                # both new terminals belong to this same node
                # add both new terminals to the terminal intersections above
                for intersection in iter(intersections):
                    terminalIntersections.add(intersection)
                # update the nodeIntersected with
                nodesIntersectedWith.add(nodeID)

        if len(nodesIntersectedWith) == 0 and len(terminalIntersections) == 0:
            # the new connection doesn't belong to any old node
            # create a new node for it
            node = self.createNewCircuitNode(
                nodeCount=len(self.circuitNodes),
                componentTerminals=self.selectedTerminals,
            )
            return node
        elif len(nodesIntersectedWith) == 1 and len(terminalIntersections) == 1:
            # connection is already part of a single node.
            # we add the new terminal that's not already part of that node, to the node
            # get the nodeID
            nodeID = next(iter(nodesIntersectedWith))
            # get the terminals involved in the node
            componentTerminals = self.circuitNodes.get(nodeID).componentTerminals.copy()
            for newComponentTerminal in self.selectedTerminals:
                componentTerminals.append(newComponentTerminal)
            # remove duplicates
            componentTerminals = list(set(componentTerminals))
            # set the componentTerminals of the node to the new componentTerminals
            self.circuitNodes.get(nodeID).componentTerminals = componentTerminals
            return self.circuitNodes.get(nodeID)
        elif len(nodesIntersectedWith) == 1 and len(terminalIntersections) == 2:
            # parallel connection between the two components involved
            print("PARALLEL CONNECTION")
        elif len(nodesIntersectedWith) == 2 and len(terminalIntersections) == 2:
            # short circuit between the two nodes
            print("SHORT CIRCUIT BETWEEN NODE")

    def createNewCircuitNode(
        self, nodeCount: int, componentTerminals: List[Tuple[str, int]]
    ):
        """
        Function that creates a new node and updates the circuitNodes of the canvas
        from nodeCount and componentTerminals involved in connection.
        """
        # create a node
        newCircuitNode = CircuitNode(nodeCount=nodeCount)
        for componentTerminal in componentTerminals:
            newCircuitNode.componentTerminals.append(componentTerminal)
        # add new node to the dict of nodes
        self.circuitNodes[newCircuitNode.uniqueID] = newCircuitNode
        return newCircuitNode

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

from typing import Type, Dict, List, Tuple

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt

from components.general import GeneralComponent
from components.wire import Wire, ComponentAndTerminalIndex
from SimulationBackend.middleware import CircuitNode
from SimulationBackend.circuit_simulator import CircuitSimulator


class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.wireToolActive = False
        self.selectedTerminals = []

        self.components: Dict[str, GeneralComponent] = {}
        self.wires: Dict[str, Wire] = {}

        # dictionary to store circuit nodes based on their uniqueIDs
        self.circuitNodes: Dict[str, CircuitNode] = {}

        self.initUI()

    def initUI(self):
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(Qt.GlobalColor.black)

    def updateEverything(self):
        print("updating everything")
        # updating all wires
        for wireID in self.wires.keys():
            self.wires.get(wireID).update()

    def addComponent(self, component: Type["GeneralComponent"]) -> None:
        comp = component(compCount=len(self.components))
        try:
            comp.signals.terminalClicked.connect(self.onTerminalClick)
            print("terminal click signal connected")
        except Exception as e:
            ...
        self.scene().addItem(comp)
        self.components[comp.uniqueID] = comp

    def onWireToolClick(self, wireToolState: bool):
        self.wireToolActive = wireToolState
        if not self.wireToolActive:
            self.selectedTerminals = []

    def onTerminalClick(self, uniqueID: str, terminalIndex: int):
        print(f"terminal {terminalIndex} of {uniqueID} clicked!")
        print(self.selectedTerminals)
        if self.wireToolActive:
            clickedTerminal = (uniqueID, terminalIndex)
            if clickedTerminal in self.selectedTerminals:
                print("terminal already in list")
                return
            self.selectedTerminals.append(clickedTerminal)

            if len(self.selectedTerminals) == 2:
                self.drawWire()
                self.selectedTerminals = []

        print("after terminal click:", self.selectedTerminals)

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

        print(results)

        # set the simulated node voltages
        self.setSimulatedNodeVoltages(results=results)
        self.updateEverything()

    def setSimulatedNodeVoltages(
        self, results: Dict[str, Dict[str, List[str]]]
    ) -> None:
        voltages = results.get("voltages")
        for nodeID in self.circuitNodes.keys():
            nodeData = voltages.get(nodeID.lower())
            # add node data to the node
            self.circuitNodes.get(nodeID).data = {"V": nodeData}

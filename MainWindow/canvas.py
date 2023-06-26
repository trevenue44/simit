from typing import Type, Dict, List, Tuple

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt

from components.general import GeneralComponent
from components.wire import Wire, ComponentAndTerminalIndex
from SimulationBackend.middleware import CircuitNode


class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.wireToolActive = False
        self.selectedTerminals = []

        self.components = {}
        self.wires = {}

        # dictionary to store circuit nodes based on their uniqueIDs
        self.circuitNodes: Dict[str, CircuitNode] = {}

        self.initUI()

    def initUI(self):
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(Qt.GlobalColor.black)

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
        print("drawing wire")
        start = ComponentAndTerminalIndex(
            self.components.get(self.selectedTerminals[0][0]),
            self.selectedTerminals[0][1],
        )
        end = ComponentAndTerminalIndex(
            self.components.get(self.selectedTerminals[1][0]),
            self.selectedTerminals[1][1],
        )
        wire = Wire(start, end)
        self.scene().addItem(wire)
        print("after_drawing: ", self.selectedTerminals)
        # add new connection to existing nodes or create new nodes
        self.updateCircuitNodes()

        # ######### print put current state of nodes
        print("===========CIRCUIT NODES==========")
        for circuitNode in self.circuitNodes.values():
            print(circuitNode.uniqueID)
            print(circuitNode.componentTerminals)
            print("")
        ##############################

    def updateCircuitNodes(self):
        if len(self.circuitNodes) == 0:
            # there are no existing nodes
            # create a new node
            self.createNewCircuitNode(
                nodeCount=len(self.circuitNodes),
                componentTerminals=self.selectedTerminals,
            )
            return

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
            self.createNewCircuitNode(
                nodeCount=len(self.circuitNodes),
                componentTerminals=self.selectedTerminals,
            )
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

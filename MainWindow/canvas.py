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
        # create or update nodes after drawing wire
        print("creating/updating nodes")

        # get current number of nodes for uniqueID
        nodeCount = len(self.circuitNodes)
        if nodeCount == 0:
            # create new node if there isn't any in there already.
            self.createNewCircuitNode(
                nodeCount=nodeCount, componentTerminals=self.selectedTerminals
            )
            # exit out of fxn
            return

        intersections = set()
        nodesIntersectedWith: List[str] = []

        # if there are existing nodes
        for nodeID in self.circuitNodes.keys():
            # check to see if new connection is part of an existing node
            existingNode = self.circuitNodes.get(nodeID)

            existingTerminalsSet = set(existingNode.componentTerminals)
            newTerminalsSet = set(self.selectedTerminals)

            # intersection of component terminals of existing nodes and new connection would tell if new connection belongs to an existing node
            # possible that it would contain more than one
            # this will occur in parrallel connections
            intersection = existingTerminalsSet.intersection(newTerminalsSet)

            if len(intersections) != 0:
                # if there's at least one intersection with the node,
                # keep track of the node
                nodesIntersectedWith.append(nodeID)

            # keep track of all the intersections
            intersections = intersections.union(intersection)

        # if new connection belongs to and existing node
        if len(intersections) == 1 and len(nodesIntersectedWith) == 1:
            # append the componentTerminal that is NOT already in the componentTerminals of the node.
            newTerminalSet = newTerminalsSet.difference(intersection)
            for terminal in iter(newTerminalSet):
                self.circuitNodes.get(nodeID).componentTerminals.append(terminal)
        elif len(intersections) == 2 and len(nodesIntersectedWith) == 2:
            # there is a short ciruit
            # there new connection intersects with more than one node
            ...
        elif len(intersections) == 2 and len(nodesIntersectedWith) == 1:
            # there is a parallel connection between the two components whose terminals are involved.
            # what should we do??
            ...
        elif len(intersections) == 0 and len(nodesIntersectedWith) == 0:
            # if new connection doesn't belong to an existing node
            # create a new node
            self.createNewCircuitNode(
                nodeCount=nodeCount, componentTerminals=self.selectedTerminals
            )

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

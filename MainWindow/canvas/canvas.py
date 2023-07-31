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
        self.selectedWireIDs: List[str] = []

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
        """
        Function to create and add a component to the scene.

        Params:
            component: `Type[GeneralComponent]` the component to add to the scene

        Returns:
            `None`
        """
        # generate the unique count for the component
        uniqueCount = self.generateUniqueComponentCount(component.name)
        # create the component
        comp = component(compCount=uniqueCount)
        try:
            comp.signals.terminalClicked.connect(self.onTerminalClick)
            comp.signals.componentSelected.connect(self.onComponentSelected)
            comp.signals.componentDeselected.connect(self.onComponentDeselected)
        except Exception as e:
            print(f"[INFO] Some component signals not connected - Error: {e}")
        self.scene().addItem(comp)
        self.components[comp.uniqueID] = comp

    def generateUniqueComponentCount(self, componentName: str) -> int:
        """
        Function to generate the unique component count for a component name.

        Params:
            componentName: `str` the name of the component to generate the unique count for

        Returns:
            `int` the unique count for the component name
        """
        # get all the componentIDs availble
        existingIDs = self.components.keys()
        # filter the IDs to get only the ones that start with the component name
        filteredIDs = list(filter(lambda x: x.startswith(componentName), existingIDs))
        # if there are no existing IDs, return 0
        if len(filteredIDs) == 0:
            return 0
        # sort the IDs in ascending order
        filteredIDs.sort()
        # get the last ID
        lastID = filteredIDs[-1]
        # get the unique count from the last ID
        uniqueCount = int(lastID.split("-")[-1])
        # increment the unique count by 1
        uniqueCount += 1
        return uniqueCount

    def deleteComponents(self, componentIDs: List[str]):
        for componentID in componentIDs:
            component = self.components.get(componentID)
            if component is not None:
                # go through circuit nodes and remove the component terminals from the nodes
                for node in component.terminalNodes.values():
                    node.removeComponent(componentID)
                # remove component from scene
                self.scene().removeItem(component)
                # delete component from the components list
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

    def onWireSelected(self, uniqueID: str):
        self.selectedWireIDs.append(uniqueID)

    def onWireDeselected(self, uniqueID: str):
        self.selectedWireIDs.remove(uniqueID)

    def deleteWires(self, wireIDs: List[str]):
        """
        Function that deletes all wires along with connected wires and related nodes.

        Params:
            wireIDs: `List[str]` - a list of the IDs of the wires to delete

        Returns:
            None
        """
        for wireID in wireIDs:
            # get the wire
            wire = self.wires.get(wireID)
            if wire is not None:
                # get the related node
                node = wire.circuitNode
                if node is not None:
                    # get and delete all related wires
                    for relatedWire in node.wires:
                        # remove related wire from wires on canvas
                        if relatedWire.uniqueID in self.wires.keys():
                            del self.wires[relatedWire.uniqueID]
                        # remove relatedWire from scene
                        if relatedWire in self.scene().items():
                            self.scene().removeItem(relatedWire)
                    # remove node from circuit nodes on canvas
                    if node.uniqueID in self.circuitNodes.keys():
                        del self.circuitNodes[node.uniqueID]
                # remove wire from scene
                if wire in self.scene().items():
                    self.scene().removeItem(wire)
        self.scene().update()

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
        """
        Handles the event of a terminal being clicked in the user interface. This function
        is responsible for creating new Wire objects when necessary and updating their start
        and end points according to the terminals that are clicked. It also handles
        connecting wire signals and updating circuit nodes.

        Params:
            uniqueID (str): Unique ID of the component.
            terminalIndex (int): Index of the terminal that has been clicked.
        """
        # Only proceed if the wire tool is active.
        if not self.wireToolActive:
            return

        # Fetch the component associated with the uniqueID.
        component = self.components.get(uniqueID)

        # If no wire or terminal is currently selected, start a new wire from the clicked terminal.
        if self.currentWire is None and len(self.clickedTerminals) == 0:
            self._initiateWireOnTerminalClick(component, terminalIndex)

        # If there's an active wire and one terminal has been clicked, set the end of the wire
        # to the newly clicked terminal and update the circuit accordingly.
        elif self.currentWire is not None and len(self.clickedTerminals) == 1:
            self._finalizeWireOnTerminalClick(component, terminalIndex)

    def _initiateWireOnTerminalClick(self, component: GeneralComponent, terminalIndex):
        """
        Initiates a wire from the specified terminal of the given component.

        Params:
            component (Component): Component from which the wire is initiated.
            terminalIndex (int): Index of the terminal from which the wire is initiated.
        """
        # Create new wire and assign start position.
        self.currentWire = Wire(
            start=ComponentAndTerminalIndex(component, terminalIndex),
            wireCount=len(self.wires),
        )

        # Connect signals for wire interaction events.
        self.currentWire.signals.wireClicked.connect(self.onWireClick)
        self.currentWire.signals.wireSelected.connect(self.onWireSelected)
        self.currentWire.signals.wireDeselected.connect(self.onWireDeselected)

        # Register the clicked terminal.
        self.clickedTerminals.append((component.uniqueID, terminalIndex))

    def _finalizeWireOnTerminalClick(self, component: GeneralComponent, terminalIndex):
        """
        Finalizes the active wire to the specified terminal of the given component
        and updates the circuit accordingly.

        Params:
            component (Component): Component to which the wire is finalized.
            terminalIndex (int): Index of the terminal to which the wire is finalized.
        """
        # Register terminal click and prevent connecting a wire to the same terminal twice.
        terminal = (component.uniqueID, terminalIndex)
        if terminal not in self.clickedTerminals:
            # Set wire end position.
            self.currentWire.setEnd(
                end=ComponentAndTerminalIndex(component, terminalIndex)
            )

            # Register the clicked terminal.
            self.clickedTerminals.append(terminal)

            # Register the completed wire and clear current wire.
            self.wires[self.currentWire.uniqueID] = self.currentWire

            # Update nodes when connection is done and assign circuit node to wire.
            node = self.updateCircuitNodes()
            self.currentWire.setCircuitNode(node)

            # Register the new wire with the circuit node.
            node.addNewWires([self.currentWire])

            # Reset for next wire creation process.
            self.clickedTerminals.clear()
            self.currentWire = None

    def onWireClick(self, uniqueID: str, point: QPointF):
        if self.wireToolActive:
            # if the user accidentally selects the current wire he's drawing
            # the point clicked could be the start of another wire.
            # deselect wire component if wire tool is active
            wire = self.wires.get(uniqueID)
            if wire is None:
                return
            wire.setSelected(False)
            self.rerenderItem(wire)
            print("selected has been set to ", wire.isSelected())

            if self.currentWire is None and len(self.clickedTerminals) == 0:
                # user about to draw a new wire
                self.currentWire = Wire(
                    start=(wire, point),
                    wireCount=len(self.wires),
                )
                # connect wire clicked signal
                self.currentWire.signals.wireClicked.connect(self.onWireClick)
                self.currentWire.signals.wireSelected.connect(self.onWireSelected)
                self.currentWire.signals.wireDeselected.connect(self.onWireDeselected)
                self.clickedTerminals.append((uniqueID, QPointF))
            elif self.currentWire is not None and len(self.clickedTerminals) == 1:
                # making sure same terminal is not clicked twice when drawing a wire
                if uniqueID != self.clickedTerminals[0][0]:
                    self.currentWire.setEnd(end=(wire, point))
                    self.clickedTerminals.append((uniqueID, QPointF))
                    # add wire to the completed wires dictionary to keep track of it
                    self.wires[self.currentWire.uniqueID] = self.currentWire
                    # update nodes when connection is done
                    node = self.updateCircuitNodes()
                    self.currentWire.setCircuitNode(node)
                    # add wire to node
                    node.addNewWires([self.currentWire])
                    # clear the content of the clicked terminals list
                    self.clickedTerminals.clear()
                    self.currentWire = None

    def updateCircuitNodes(self):
        if len(self.circuitNodes) == 0:
            # there are no existing nodes
            # create a new node
            node = self.createNewCircuitNode(
                nodeCount=len(self.circuitNodes),
                componentTerminals=self.clickedTerminals,
            )
            return node

        # deal with situations wheere at least one side of the connection is a wire (already from a node)
        wireTerminals = list(
            filter(lambda t: "wire" in t[0].lower(), self.clickedTerminals)
        )

        if len(wireTerminals) > 2:
            print("PROBLEM!!")
        elif len(wireTerminals) == 2:
            # there is a short circuit
            # two, already existing wires, have been connnected.
            # combine the two nodes into one node.
            # get the wires first
            wire1 = self.wires.get(wireTerminals[0][0])
            wire2 = self.wires.get(wireTerminals[1][0])
            # get the respective nodes of the wires
            node1 = wire1.circuitNode
            node2 = wire2.circuitNode
            # if the nodes are the same, just return one of them
            if node1 == node2:
                return node1
            # combine the component terminals into node1
            node = node1.combineWith(node2)
            # remove node2 after combing it onto noe1
            if node2.uniqueID in self.circuitNodes.keys():
                del self.circuitNodes[node2.uniqueID]
            return node
        elif len(wireTerminals) == 1:
            # get the component
            componentTerminalInClickedTerminals = (
                self.clickedTerminals[0]
                if self.clickedTerminals[1] in wireTerminals
                else self.clickedTerminals[1]
            )
            component = self.components.get(componentTerminalInClickedTerminals[0])
            # check to see if component terminal is already part of a node
            terminalNode = component.terminalNodes.get(
                componentTerminalInClickedTerminals[1]
            )
            # get the wire
            wire = self.wires.get(wireTerminals[0][0])
            # get the node the wire already belongs to
            wireNode = wire.circuitNode
            if terminalNode is None:
                # a new component is about to be added to an already existing node (wire)
                # update the current node with the new component
                wireNode.addComponentTerminals([componentTerminalInClickedTerminals])
            else:
                # component terminal already belongs to a node
                # combine terminalNode onto wireNode
                wireNode.addComponentTerminals(terminalNode.componentTerminals)
            # update the terminal nodes of the component
            component.setTerminalNode(componentTerminalInClickedTerminals[1], wireNode)
            # return node as the final node for the newly created wire
            return wireNode

        # keep track of the newTerminals that are already node(s)
        terminalIntersections: set = set()
        # keep track of the nodes the new terminals intersect with
        nodesIntersectedWith: set = set()

        # if there are already circuitNodes
        # loops through the circuit nodes
        for nodeID in self.circuitNodes.keys():
            circuitNode = self.circuitNodes.get(nodeID)
            # compare the terminals involved in each node to the terminals involved in the new conection
            newTerminals = set(self.clickedTerminals)
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
                componentTerminals=self.clickedTerminals,
            )
            # update the terminal nodes of the components
            for componentID, terminalIndex in self.clickedTerminals:
                component = self.components.get(componentID)
                component.setTerminalNode(terminalIndex, node)
            # return newly created node as the node of the newly created wire.
            return node
        elif len(nodesIntersectedWith) == 1 and len(terminalIntersections) == 1:
            # connection is already part of a single node.
            # we add the new terminal that's not already part of that node, to the node
            # get the nodeID
            nodeID = next(iter(nodesIntersectedWith))
            # get the node
            node = self.circuitNodes.get(nodeID)
            # add both terminals to the terminals of the node
            # duplicates are automatically handled by the node
            node.addComponentTerminals(self.clickedTerminals)
            # update the terminal nodes of the components
            for componentID, terminalIndex in self.clickedTerminals:
                component = self.components.get(componentID)
                component.setTerminalNode(terminalIndex, node)
            # return newly created node as the node of the newly created wire.
            return node
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

    def rerenderItem(self, item) -> None:
        if item in self.scene().items():
            self.scene().removeItem(item)
        self.scene().addItem(item)
        self.scene().update()

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
                self.rerenderItem(self.currentWire)

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

        print("######## Circuit Nodes #############")
        for id, node in self.circuitNodes.items():
            print(id, [wire.uniqueID for wire in node.wires])
        print("####################################")

        return

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

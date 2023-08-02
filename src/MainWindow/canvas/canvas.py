from typing import Type, Dict, List, Tuple
from PyQt6 import QtGui

from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPointF

from .grid_scene import GridScene
from components.general import GeneralComponent
from components.general.component_and_terminal_index import ComponentAndTerminalIndex
from components.wire import Wire

from SimulationBackend.middleware import CircuitNode
from SimulationBackend.circuit_simulator import CircuitSimulator

import constants
from logger import logger


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
            logger.exception("Some component signals not connected")
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
        """
        for wireID in wireIDs:
            # Don't preceed if the wire doesn't exist
            wire = self.wires.get(wireID)
            if wire is None:
                continue

            # remove wire from scene
            if wire in self.scene().items():
                self.scene().removeItem(wire)

            # Don't preceed if the wire is not connected to a node
            node = wire.circuitNode
            if node is None:
                continue

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

            # Register the completed wire.
            self.wires[self.currentWire.uniqueID] = self.currentWire

            # Update nodes when connection is done and assign circuit node to wire.
            node = self.update_circuit_nodes()
            self.currentWire.setCircuitNode(node)

            # Register the new wire with the circuit node.
            node.addNewWires([self.currentWire])

            # Reset for next wire creation process.
            self.clickedTerminals.clear()
            self.currentWire = None

    def onWireClick(self, uniqueID: str, point: QPointF):
        """
        Handles the event of a wire being clicked in the user interface. This function
        is responsible for creating new Wire objects when necessary and updating their start
        and end points according to the terminals that are clicked. It also handles
        connecting wire signals and updating circuit nodes.

        Params:
            uniqueID (str): Unique ID of the wire.
            point (QPointF): Point on the wire that has been clicked.

        """
        # Only proceed if the wire tool is active.
        if not self.wireToolActive:
            return

        # Fetch the wire associated with the uniqueID.
        wire = self.wires.get(uniqueID)

        # if wire is not found, log the error and return
        if wire is None:
            logger.error(f"Wire with uniqueID {uniqueID} not found")
            return

        # If no wire or terminal is currently selected, start a new wire from the clicked wire.
        if self.currentWire is None and len(self.clickedTerminals) == 0:
            self._initialize_wire_on_wire_click(wire, point)

        # If there's an active wire and one terminal has been clicked, set the end of the wire
        # to the newly clicked wire and update the circuit accordingly.
        elif self.currentWire is not None and len(self.clickedTerminals) == 1:
            self._finalize_wire_on_wire_click(wire, point)

    def _initialize_wire_on_wire_click(self, wire: "Wire", point: QPointF):
        """
        Initiates a wire from the specified wire point.

        Params:
            wire (`Wire`): Wire from which the wire is initiated.
            point (`int`): Point on the wire from which new wire is initiated.
        """
        # Create new wire and assign start position.
        self.currentWire = Wire(
            start=(wire, point),
            wireCount=len(self.wires),
        )
        # Connect signals for wire interaction events.
        self.currentWire.signals.wireClicked.connect(self.onWireClick)
        self.currentWire.signals.wireSelected.connect(self.onWireSelected)
        self.currentWire.signals.wireDeselected.connect(self.onWireDeselected)

        # Register the clicked wire.
        self.clickedTerminals.append((wire.uniqueID, QPointF))

    def _finalize_wire_on_wire_click(self, wire: "Wire", point: QPointF):
        """
        Finalizes the active wire to the specified wire point
        and updates the circuit accordingly.

        Params:
            wire (`Wire`): Wire to which the wire is finalized.
            point (`int`): Point on the wire to which the wire is finalized.
        """
        # Makes sure that the same wire is not used as both start and end of a wire
        # Get the uniqueIDs of the wires currently in the clicked terminals
        wireIDs = [terminal[0] for terminal in self.clickedTerminals]

        # Only proceed if the wire is not already in the clicked terminals
        if wire.uniqueID in wireIDs:
            return

        # Set wire end position.
        self.currentWire.setEnd(end=(wire, point))

        # Register the clicked wire in the clicked terminals
        self.clickedTerminals.append((wire.uniqueID, QPointF))

        # Register the completed wire
        self.wires[self.currentWire.uniqueID] = self.currentWire

        # Update nodes when connection is done and assign circuit node to wire.
        node = self.update_circuit_nodes()
        self.currentWire.setCircuitNode(node)

        # Register the new wire with the circuit node.
        node.addNewWires([self.currentWire])

        # Reset for next wire creation process.
        self.clickedTerminals.clear()
        self.currentWire = None

    def rerenderItem(self, item) -> None:
        if item in self.scene().items():
            self.scene().removeItem(item)
        self.scene().addItem(item)
        self.scene().update()

    def update_circuit_nodes(self) -> CircuitNode | None:
        """Updates the circuit nodes based on various conditions"""
        if not self.circuitNodes:
            return self._create_new_node_if_no_existing_nodes()

        wireTerminals = self._filter_wire_terminals()
        wire_terminals_len = len(wireTerminals)

        if wire_terminals_len > 2:
            logger.critical("More than 2 terminals registered on canvas")
            return
        elif wire_terminals_len == 2:
            return self._handle_wire_short_circuit(wireTerminals)
        elif wire_terminals_len == 1:
            return self._handle_single_wire_terminal(wireTerminals)

        return self._update_node_or_create_new_one_if_no_wire_terminals()

    def _create_new_node_if_no_existing_nodes(self) -> CircuitNode:
        """Creates a new node if there are no existing nodes"""
        node = CircuitNode(len(self.circuitNodes))
        node.addComponentTerminals(self.clickedTerminals)

        # Register the newly created node
        self.circuitNodes[node.uniqueID] = node
        for componentID, terminalIndex in self.clickedTerminals:
            component = self.components.get(componentID)
            component.setTerminalNode(terminalIndex, node)

        return node

    def _filter_wire_terminals(self):
        """filters wire terminals from clicked termminals"""
        return list(filter(lambda t: "wire" in t[0].lower(), self.clickedTerminals))

    def _handle_wire_short_circuit(self, wireTerminals: List[Tuple[str, int]]):
        """handle short circuit scenario when two wires are connected and merges two nodes into one"""
        # Get the wires first
        wire1 = self.wires.get(wireTerminals[0][0])
        wire2 = self.wires.get(wireTerminals[1][0])
        # Get the respective nodes of the wires
        node1 = wire1.circuitNode
        node2 = wire2.circuitNode
        # If the nodes are the same, just return one of them
        if node1 == node2:
            return node1
        # Combine the component terminals into node1
        node = node1.combineWith(node2)
        # Remove node2 after combing it onto noe1
        if node2.uniqueID in self.circuitNodes.keys():
            del self.circuitNodes[node2.uniqueID]
        return node

    def _handle_single_wire_terminal(self, wireTerminals: List[Tuple[str, int]]):
        """handles scenerio with a single wire terminal connected to a component terminal"""
        componentTerminalInClickedTerminals = (
            self.clickedTerminals[0]
            if self.clickedTerminals[1] in wireTerminals
            else self.clickedTerminals[1]
        )
        componentID, terminalIndex = componentTerminalInClickedTerminals
        component = self.components.get(componentID)
        wireID = wireTerminals[0][0]  # [(wireID, QPoint)]
        wire = self.wires.get(wireID)

        wireNode = wire.circuitNode
        componentNode = component.terminalNodes.get(terminalIndex)

        # if the component terminal is not already part of a node, add it to the node of the wire
        if componentNode is None:
            wireNode.addComponentTerminals([componentTerminalInClickedTerminals])
            # Register the node in the component
            component.setTerminalNode(terminalIndex, wireNode)

            return wireNode
        # If the component is already part of a node, combine the two nodes into one.
        else:
            node = wireNode.combineWith(componentNode)

            # Register the new node for both the wire and the component
            wire.setCircuitNode(node)
            component.setTerminalNode(terminalIndex, node)

            return node

    def _update_node_or_create_new_one_if_no_wire_terminals(self):
        """Updates an existing node or creates a new one if connection is purely between component terminals"""
        terminalIntersections, nodesIntersectedWith = self._find_intersections()

        if not nodesIntersectedWith and not terminalIntersections:
            return self._create_new_node()
        elif len(nodesIntersectedWith) == 1 and len(terminalIntersections) == 1:
            return self._update_existing_nodes(nodesIntersectedWith)
        elif len(nodesIntersectedWith) == 1 and len(terminalIntersections) == 2:
            logger.info("Parallel Connection in connection between components")
        elif len(nodesIntersectedWith) == 2 and len(terminalIntersections) == 2:
            return self._handle_short_circuit_between_nodes(
                nodesIntersectedWith, terminalIntersections
            )

    def _find_intersections(self) -> Tuple[set, set]:
        """Finds the intersection of new terminals and old ones based on existing circuit nodes"""
        # Initialize an empty set to keep track of terminals that are already present in a node
        terminalIntersections: set = set()

        # Initialize an empty set to keep track of existing nodes that intersect with the new terminals
        nodesIntersectedWith: set = set()

        # Check if there are existing circuitNodes
        # If yes, iterate through each of these circuit nodes
        for nodeID in self.circuitNodes.keys():
            # Fetch the current circuit node based on nodeID
            circuitNode = self.circuitNodes.get(nodeID)

            # Convert the clicked terminals to a set, these are the new terminals being added
            newTerminals = set(self.clickedTerminals)

            # Convert the terminals of the current circuit node to a set, these are the existing terminals
            oldTerminals = set(circuitNode.componentTerminals)

            # Find the common terminals between new and old terminals
            intersections = newTerminals.intersection(oldTerminals)

            if len(intersections) == 0:
                # This implies that the new terminals don't intersect with the current circuit node
                # Move to the next circuit node
                continue
            elif len(intersections) == 1:
                # Only one of the new terminals intersects with the current node
                # Add this terminal to the set that keeps track of terminals intersected with
                terminalIntersections.add(next(iter(intersections)))
                # Similarly, add the current node's ID to the set that keeps track of intersected nodes
                nodesIntersectedWith.add(nodeID)
            elif len(intersections) == 2:
                # Both new terminals intersect with the current node
                # Add these terminals to the set that keeps track of terminals intersected with
                for intersection in iter(intersections):
                    terminalIntersections.add(intersection)
                # Add the current node's ID to the set that keeps track of intersected nodes
                nodesIntersectedWith.add(nodeID)

        return terminalIntersections, nodesIntersectedWith

    def _create_new_node(self) -> CircuitNode:
        """Creates a new node if the none of the clicked terminals are already part of a node"""
        return self._create_new_node_if_no_existing_nodes()

    def _update_existing_nodes(self, nodesIntersectedWith: set) -> CircuitNode:
        """Update an eisting node if the new connection is part of an existing node"""
        nodeID = next(iter(nodesIntersectedWith))
        node = self.circuitNodes.get(nodeID)
        node.addComponentTerminals(self.clickedTerminals)

        # Register the node in the components
        for componentID, terminalIndex in self.clickedTerminals:
            component = self.components.get(componentID)
            component.setTerminalNode(terminalIndex, node)

        return node

    def _handle_short_circuit_between_nodes(
        self, nodesIntersectedWith, terminalIntersections
    ) -> CircuitNode:
        """Handles short circuit scenario when two nodes are connected and merges two nodes into one"""
        # Converts the set into lists so that they can be indexed
        nodesIntersectedWith = list(nodesIntersectedWith)

        # Fetch the two nodes that are being shorted
        node1 = self.circuitNodes.get(nodesIntersectedWith[0])
        node2 = self.circuitNodes.get(nodesIntersectedWith[1])

        # Combine the shorted nodes into one
        node = node1.combineWith(node2)

        # Remove node2 after combing it onto node1
        if node2.uniqueID in self.circuitNodes.keys():
            del self.circuitNodes[node2.uniqueID]

        # Register the new node in the components
        for componentID, terminalIndex in iter(terminalIntersections):
            component = self.components.get(componentID)
            component.setTerminalNode(terminalIndex, node)

        return node

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
        logger.info("Simulating...")

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

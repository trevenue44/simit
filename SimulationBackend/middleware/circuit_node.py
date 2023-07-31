from typing import List, Tuple, Dict, TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSignal


if TYPE_CHECKING:
    from components import Wire


class CircuitNode:
    name = "CircuitNode"

    class Signals(QObject):
        nodeDataChanged = pyqtSignal()

    def __init__(self, nodeCount: int) -> None:
        self.uniqueID = f"{self.name}-{nodeCount}"

        self.componentTerminals: List[Tuple[str, int]] = []

        # keep track of wires that make up the node
        self.wires: List["Wire"] = []

        self.data: Dict[str, List[str]] = {}

        # pyqt signals
        self.signals = self.Signals()

    def addNewWires(self, newWires: List["Wire"]):
        """
        A function to add new wires to the node

        Params:
            newWires: a list of wires to add to the node

        Returns:
            None
        """
        for newWire in newWires:
            if newWire not in self.wires:
                self.wires.append(newWire)
                # update the wire's node
                newWire.setCircuitNode(self)

    def removeWires(self, wires: List["Wire"]):
        """
        A function to remove wires from the node

        Params:
            wires: a list of wires to remove from the node

        Returns:
            None
        """
        for wire in wires:
            if wire in self.wires:
                self.wires.remove(wire)
                # update the wire's node
                wire.setCircuitNode(None)

    def setNodeData(self, key, value):
        """
        A function that sets the node values after simulation. Voltage and the likes.

        Params:
            key: string - the particular node parameter to set
            value: string - the value of the paramter specified in key
        """
        self.data[key] = value
        self.signals.nodeDataChanged.emit()

    def addComponentTerminals(self, newComponentTerminals: List[Tuple[str, int]]):
        """
        A function to add component terminal tuples to the componentTerminals list and ensure that there are no duplicates

        Params:
            newComponentTerminals: a list of tuples of the component terminals. Each tuple if the component uniqueID
            and the terminal index

        Returns:
            None
        """
        for newComponentTerminal in newComponentTerminals:
            if newComponentTerminal not in self.componentTerminals:
                self.componentTerminals.append(newComponentTerminal)

    def combineWith(self, otherNode: "CircuitNode"):
        """
        A function that combines this circuit node with another one and returns the combined version

        Params:
            otherCircuitNode - another circuit node instance to be combined with this one

        Returns:
            The combined circuit node instance
        """
        # add the terminals of the other node to current node terminals
        self.addComponentTerminals(otherNode.componentTerminals)

        # update the nodes of the wires in the other node to this node
        for wire in otherNode.wires:
            wire.setCircuitNode(self)
            # add the wire to this node's wires
            self.addNewWires([wire])

        # return this node as the combine version
        return self

    def removeComponent(self, uniqiueID: str) -> bool:
        """
        A function to check the compoonent terminals attribute to see if the component with the specified uniqueID is
        connected to the node and removes it from the node

        Params:
            uniqueID: string - the uniqueID of the component to check

        Returns:
            `True` if the component is connected to the node and removes it from the componentTerminals, `False` otherwise
        """
        for componentTerminal in self.componentTerminals:
            if componentTerminal[0] == uniqiueID:
                # remove the component terminal from the list
                self.componentTerminals.remove(componentTerminal)
                return True
        return False

from typing import List, Tuple, Dict

from PyQt6.QtCore import QObject, pyqtSignal


class CircuitNode:
    name = "CircuitNode"

    class Signals(QObject):
        nodeDataChanged = pyqtSignal()

    def __init__(self, nodeCount: int) -> None:
        self.uniqueID = f"{self.name}-{nodeCount}"
        self.componentTerminals: List[Tuple[str, int]] = []
        self.data: Dict[str, List[str]] = {}

        # pyqt signals
        self.signals = self.Signals()

    def setNodeData(self, key, value):
        self.data[key] = value
        self.signals.nodeDataChanged.emit()

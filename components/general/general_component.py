from typing import Tuple

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsObject
from PyQt6.QtCore import pyqtSignal, QPointF


class GeneralComponent(QGraphicsItem):
    name: str = ...

    class Signals(QGraphicsObject):
        # signal sends (uniqueID, terminalIndex) as arguments.
        terminalClicked = pyqtSignal(str, int)
        componentMoved = pyqtSignal()

    def __init__(self, compCount: int, parent=None) -> None:
        # generate the uniqueID using the component name and the count.
        # eg. Resistor-23
        self.uniqueID = f"{self.name}-{compCount}"

        # a signals object attribute of the instance to send appropriate signals from different resistors
        self.signals = self.Signals()

        return super(GeneralComponent, self).__init__(parent)

    def getTerminalPositions(self) -> Tuple[QPointF, QPointF]:
        ...

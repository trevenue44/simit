from typing import List

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QStaticText, QFont

from components.general import ComponentAndTerminalIndex
from SimulationBackend.middleware import CircuitNode


class Wire(QGraphicsItem):
    name = "Wire"

    def __init__(
        self,
        start: ComponentAndTerminalIndex,
        end: ComponentAndTerminalIndex,
        wireCount: int,
        parent: QGraphicsItem | None = None,
    ) -> None:
        super(Wire, self).__init__(parent)

        self.uniqueID = f"{self.name}-{wireCount}"

        self.setZValue(10)

        self.start = start
        self.end = end

        self.startPos = None
        self.endPos = None

        # connect componentMoved signals
        self.start.component.signals.componentMoved.connect(
            self._extractTerminalPositions
        )
        self.end.component.signals.componentMoved.connect(
            self._extractTerminalPositions
        )

        self.circuitNode = None

        self._extractTerminalPositions()

        # Initialize the text item
        self.textItem = QGraphicsTextItem(self)
        self.textItem.setDefaultTextColor(Qt.GlobalColor.yellow)
        self.textItem.setFont(QFont("Arial", 10))
        self.textItem.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)

    def _extractTerminalPositions(self):
        self.startPos = self.start.component.getTerminalPositions()[
            self.start.terminalIndex
        ]
        self.endPos = self.end.component.getTerminalPositions()[self.end.terminalIndex]
        self.update()
        if self.scene():
            self.scene().update()

    def boundingRect(self) -> QRectF:
        return QRectF(self.startPos, self.endPos).normalized()

    def paint(self, painter, option, widget):
        if self.startPos is None or self.endPos is None:
            return

        pen = QPen(Qt.GlobalColor.gray, 1.5, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.startPos, self.endPos)

        # write simulation results if there is some
        if self.circuitNode:
            # calculate the midpoint of the wire
            midpoint = (self.startPos + self.endPos) / 2

            text = f"CN-{self.circuitNode.uniqueID.split('-')[-1]}"

            if self.getNodeVoltage():
                # get node data
                # eg: ["10.00", "V"]
                nodeVoltage = self.getNodeVoltage()
                # combine value and unit into one text
                text = f"{text}\n{' '.join(nodeVoltage)}"

            # set text and initial position
            self.textItem.setPlainText(text)
            self.textItem.setPos(midpoint)

            # Adjust the position of the text item to center it horizontally
            textWidth = self.textItem.boundingRect().width()
            self.textItem.setPos(midpoint.x() - textWidth / 2, midpoint.y())

    def getNodeVoltage(self) -> List[str] | None:
        if self.circuitNode:
            return self.circuitNode.data.get("V")
        return None

    def setCircuitNode(self, circuitNode: CircuitNode) -> None:
        self.circuitNode = circuitNode
        self.update()

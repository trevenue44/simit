import typing
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen

from components.general import ComponentAndTerminalIndex


class Wire(QGraphicsItem):
    def __init__(
        self,
        start: ComponentAndTerminalIndex,
        end: ComponentAndTerminalIndex,
        parent: QGraphicsItem | None = None,
    ) -> None:
        super(Wire, self).__init__(parent)

        self.setZValue(1)

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

        self._extractTerminalPositions()

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

        pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.startPos, self.endPos)

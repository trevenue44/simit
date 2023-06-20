import typing
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QPen


class ComponentAndTerminalIndex:
    def __init__(self, component: QGraphicsItem, terminal_index: int) -> None:
        self.component = component
        self.terminal_index = terminal_index


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

        self.start_pos = None
        self.end_pos = None

        # connect componentMoved signal
        self.start.component.signals.componentMoved.connect(
            self._extract_terminal_positions
        )
        self.end.component.signals.componentMoved.connect(
            self._extract_terminal_positions
        )

        self._extract_terminal_positions()

    def _extract_terminal_positions(self):
        print("extract_terminal_positions")
        self.start_pos = self.start.component.getTerminalPositions()[
            self.start.terminal_index
        ]
        self.end_pos = self.end.component.getTerminalPositions()[
            self.end.terminal_index
        ]
        self.update()
        if self.scene():
            self.scene().update()

    def boundingRect(self) -> QRectF:
        return QRectF(self.start_pos, self.end_pos).normalized()

    def paint(self, painter, option, widget):
        if self.start_pos is None or self.end_pos is None:
            return

        pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.start_pos, self.end_pos)

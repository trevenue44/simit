from typing import Tuple
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen

from .general import GeneralComponent
from .types import ComponentCategory


class Ground(GeneralComponent):
    name = "GND"
    category = ComponentCategory.SOURCE

    def __init__(self, compCount: int, parent=None) -> None:
        super().__init__(compCount, parent)

        # Geometry specifications of the voltage source
        self.w = 35
        self.h = 45
        self.terminalLength = 30
        self.padding = 7

    def boundingRect(self) -> QRectF:
        return QRectF(
            -self.padding,
            -self.padding,
            self.w + (2 * self.padding),
            self.h + (2 * self.padding),
        )

    def paint(self, painter: QPainter, option, widget) -> None:
        super().paint(painter, option, widget)

        pen = QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        body_h = self.h - self.terminalLength

        # get endpoints of horizontal line 1
        l1_a = QPointF(0, self.terminalLength)
        l1_b = QPointF(self.w, self.terminalLength)
        # draw horizontal line 1
        painter.drawLine(l1_a, l1_b)

        # get endpoints of horizontal line 2
        l2_a = QPointF(self.w / 5, self.terminalLength + body_h / 2)
        l2_b = QPointF((4 * self.w) / 5, self.terminalLength + body_h / 2)
        # draw horizontal line 2
        painter.drawLine(l2_a, l2_b)

        # get endpoints of horizontal line 3
        l3_a = QPointF((2 * self.w) / 5, self.terminalLength + body_h)
        l3_b = QPointF((3 * self.w) / 5, self.terminalLength + body_h)
        # draw horizontal line 3
        painter.drawLine(l3_a, l3_b)

        # get endpoints of terminal
        t_a = QPointF(self.w / 2, 0)
        t_b = QPointF(self.w / 2, self.terminalLength)
        # draw terminal
        painter.drawLine(t_a, t_b)

    def getTerminalPositions(self) -> Tuple[QPointF, QPointF]:
        t_pos = self.mapToScene(self.w / 2, 0)
        return (t_pos,)

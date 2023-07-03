from typing import Optional, Tuple

from PyQt6.QtGui import QPen, QPainter
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF

from .general import GeneralComponent


class Resistor(GeneralComponent):
    name = "Resistor"

    def __init__(self, compCount: int, parent=None):
        super(Resistor, self).__init__(compCount, parent)

        # Geometric specifications of the component. Used in drawing too
        self.w = 70
        self.h = 20
        self.terminalLength = 15

        # update data attribute
        self.data = {"R": [100.00, "kOhm"]}

    def paint(self, painter: QPainter, option, widget):
        super().paint(painter, option, widget)
        pen = QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        body_w = self.w - (2 * self.terminalLength)

        # Get the 4 cornors of the rectangle in the resistor
        point_a = QPointF(self.terminalLength, 0)
        point_b = QPointF(self.terminalLength + body_w, 0)
        point_c = QPointF(point_b.x(), point_b.y() + self.h)
        point_d = QPointF(point_a.x(), point_a.y() + self.h)

        # Draw the edges of the rectangle in the resistor
        painter.drawLine(point_a, point_b)
        painter.drawLine(point_b, point_c)
        painter.drawLine(point_c, point_d)
        painter.drawLine(point_d, point_a)

        # draw the terminals
        t1_a = QPointF(0, self.h // 2)
        t1_b = QPointF(self.terminalLength, self.h // 2)
        t2_a = QPointF(self.w - self.terminalLength, self.h // 2)
        t2_b = QPointF(self.w, self.h // 2)

        # draw terminals from their endpoints
        painter.drawLine(t1_a, t1_b)
        painter.drawLine(t2_a, t2_b)

    def boundingRect(self):
        return QRectF(0, 0, self.w, self.h)

    def getTerminalPositions(self) -> Tuple[QPointF, QPointF]:
        t1_pos = self.mapToScene(0, self.h // 2)
        t2_pos = self.mapToScene(self.w, self.h // 2)
        return t1_pos, t2_pos

    def __str__(self) -> str:
        return "Resistor"

    def __repr__(self):
        return "Resistor"

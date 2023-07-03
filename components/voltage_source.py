from typing import Tuple

from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt, QPointF, QRectF

from .general import GeneralComponent


class VoltageSource(GeneralComponent):
    name = "VoltageSource"

    def __init__(self, compCount: int, parent=None) -> None:
        super().__init__(compCount, parent)

        # Geometry specifications of the voltage source
        self.w = 70
        self.h = 20
        self.terminalLength = 25
        self.padding = 7

        # update data attribute
        self.data = {"V": ["10.00", "kV"]}

    def boundingRect(self):
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

        body_w = self.w - (2 * self.terminalLength)

        # Get the end points of the 4 lines in the body
        # (long line, short line, long line, short line)

        # Long Line 1
        ll_1_a = QPointF(self.terminalLength, 0)
        ll_1_b = QPointF(self.terminalLength, self.h)
        # draw long line 1
        painter.drawLine(ll_1_a, ll_1_b)

        # Short Line 1
        sl_1_a = QPointF(self.terminalLength + body_w / 3, self.h / 4)
        sl_1_b = QPointF(self.terminalLength + body_w / 3, (3 * self.h) / 4)
        # draw long line 1
        painter.drawLine(sl_1_a, sl_1_b)

        # Long Line 2
        ll_2_a = QPointF(self.terminalLength + (2 * (body_w / 3)), 0)
        ll_2_b = QPointF(self.terminalLength + (2 * (body_w / 3)), self.h)
        # draw long line 1
        painter.drawLine(ll_2_a, ll_2_b)

        # Short Line 2
        sl_2_a = QPointF(self.terminalLength + body_w, self.h / 4)
        sl_2_b = QPointF(self.terminalLength + body_w, (3 * self.h) / 4)
        # draw long line 1
        painter.drawLine(sl_2_a, sl_2_b)

        # get the end points of the terminals and draw the terminals
        # get the endpoints of terminal 1
        t1_a = QPointF(0, self.h / 2)
        t1_b = QPointF(self.terminalLength, self.h / 2)
        # draw terminal 1
        painter.drawLine(t1_a, t1_b)

        # get the endpoints of terminal 2
        t2_a = QPointF(self.terminalLength + body_w, self.h / 2)
        t2_b = QPointF(self.w, self.h / 2)
        # draw terminal 2
        painter.drawLine(t2_a, t2_b)

        # write the voltage value
        V = self.data.get("V")
        if V:
            text = f"V = {' '.join(V)}"

            self.textItem.setPlainText(text)
            self.textItem.setPos(
                self.w / 2 - self.textItem.boundingRect().width() / 2, -20
            )

    def getTerminalPositions(self) -> Tuple[QPointF, QPointF]:
        t1_pos = self.mapToScene(0, self.h / 2)
        t2_pos = self.mapToScene(self.w, self.h / 2)
        return t1_pos, t2_pos

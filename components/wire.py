import typing
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QPen


class Wire(QGraphicsItem):
    def __init__(
        self,
        start_pos: QPointF | None = None,
        end_pos: QPointF | None = None,
        parent: QGraphicsItem | None = None,
    ) -> None:
        super(Wire, self).__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos

    def boundingRect(self) -> QRectF:
        return QRectF(self.start_pos, self.end_pos).normalized()

    def paint(self, painter, option, widget):
        if self.start_pos is None or self.end_pos is None:
            return

        pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.start_pos, self.end_pos)

        # dx = self.end_pos.x() - self.start_pos.x()
        # dy = self.end_pos.y() - self.start_pos.y()

        # if dx == 0:  # Vertical wire
        #     painter.drawLine(self.start_pos, self.end_pos)
        # elif dy == 0:  # Horizontal wire
        #     painter.drawLine(self.start_pos, self.end_pos)
        # else:  # Diagonal wire (combination of vertical and horizontal)
        #     mid_point = QPointF(self.end_pos.x(), self.start_pos.y())
        #     painter.drawLine(self.start_pos, mid_point)
        #     painter.drawLine(mid_point, self.end_pos)

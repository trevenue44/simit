from PyQt6.QtWidgets import (
    QGraphicsSceneMouseEvent,
    QWidget,
    QGraphicsItem,
    QGraphicsObject,
)
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QLineF, QObject
from components.draggable_component import DraggableComponent


# class Resistor(DraggableComponent):
#     name = "Resistor"

#     def __init__(self, parent=None):
#         super(Resistor, self).__init__(parent)
#         self.w = 70
#         self.h = 20
#         self.terminal_length = 15
#         self.setFixedSize(self.w, self.h)
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

#     def paintEvent(self, event):
#         painter = QPainter(self)

#         pen = QPen(Qt.GlobalColor.yellow, 2, Qt.PenStyle.SolidLine)

#         painter.setPen(pen)

#         body_w = self.w - (2 * self.terminal_length)

#         point_a = (self.terminal_length, 0)
#         point_b = (self.terminal_length + body_w, 0)
#         point_c = (point_b[0], point_b[1] + self.h)
#         point_d = (point_a[0], point_a[1] + self.h)

#         painter.drawLine(*point_a, *point_b)
#         painter.drawLine(*point_b, *point_c)
#         painter.drawLine(*point_c, *point_d)
#         painter.drawLine(*point_d, *point_a)

#         # draw the terminals
#         t1_a = (0, self.h // 2)
#         t1_b = (self.terminal_length, self.h // 2)
#         t2_a = (self.w - self.terminal_length, self.h // 2)
#         t2_b = (self.w, self.h // 2)

#         painter.drawLine(*t1_a, *t1_b)
#         painter.drawLine(*t2_a, *t2_b)

#         painter.end()

#     def __str__(self) -> str:
#         return self.name

#     def __repr__(self):
#         return self.name


class Resistor(QGraphicsObject):
    name = "Resistor"

    terminalClicked = pyqtSignal(QPointF)

    def __init__(self, parent=None):
        super(Resistor, self).__init__(parent)
        self.w = 70
        self.h = 20
        self.terminal_length = 15
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def boundingRect(self):
        return QRectF(0, 0, self.w, self.h)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.GlobalColor.yellow, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        body_w = self.w - (2 * self.terminal_length)

        point_a = QPointF(self.terminal_length, 0)
        point_b = QPointF(self.terminal_length + body_w, 0)
        point_c = QPointF(point_b.x(), point_b.y() + self.h)
        point_d = QPointF(point_a.x(), point_a.y() + self.h)

        painter.drawLine(point_a, point_b)
        painter.drawLine(point_b, point_c)
        painter.drawLine(point_c, point_d)
        painter.drawLine(point_d, point_a)

        # draw the terminals
        t1_a = QPointF(0, self.h // 2)
        t1_b = QPointF(self.terminal_length, self.h // 2)
        t2_a = QPointF(self.w - self.terminal_length, self.h // 2)
        t2_b = QPointF(self.w, self.h // 2)

        painter.drawLine(t1_a, t1_b)
        painter.drawLine(t2_a, t2_b)

    def get_terminal_positions(self):
        t1_pos = self.mapToScene(0, self.h // 2)
        t2_pos = self.mapToScene(self.w, self.h // 2)
        # t1_pos = QPointF(0, self.h // 2)
        # t2_pos = QPointF(self.w, self.h // 2)
        return t1_pos, t2_pos

    # def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
    #     print("mouse pressed")
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         pos = event.pos()
    #         terminal_positions = self.get_terminal_positions()
    #         if pos in terminal_positions:
    #             print("terminal clicked")
    #             self.terminalClicked.emit(pos)
    #         else:
    #             super(Resistor, self).mousePressEvent(event)

    #     # return super().mousePressEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        print("mouse pressed")
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            terminal_positions = self.get_terminal_positions()
            clicked_terminal = None
            min_distance = float(5)

            for terminal_pos in terminal_positions:
                distance = QLineF(pos, terminal_pos).length()
                print(distance)
                if distance < min_distance:
                    min_distance = distance
                    clicked_terminal = terminal_pos

            if clicked_terminal is not None:
                self.terminalClicked.emit(clicked_terminal)
            else:
                super().mousePressEvent(event)

    def __str__(self) -> str:
        return "Resistor"

    def __repr__(self):
        return "Resistor"

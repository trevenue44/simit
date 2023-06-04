from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt
from components.draggable_component import DraggableComponent


class Resistor(DraggableComponent):
    name = "Resistor"

    def __init__(self, parent=None):
        super(Resistor, self).__init__(parent)
        self.w = 70
        self.h = 20
        self.terminal_length = 15
        self.setFixedSize(self.w, self.h)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.GlobalColor.yellow, 2, Qt.PenStyle.SolidLine)

        painter.setPen(pen)

        body_w = self.w - (2 * self.terminal_length)

        point_a = (self.terminal_length, 0)
        point_b = (self.terminal_length + body_w, 0)
        point_c = (point_b[0], point_b[1] + self.h)
        point_d = (point_a[0], point_a[1] + self.h)

        painter.drawLine(*point_a, *point_b)
        painter.drawLine(*point_b, *point_c)
        painter.drawLine(*point_c, *point_d)
        painter.drawLine(*point_d, *point_a)

        # draw the terminals
        t1_a = (0, self.h // 2)
        t1_b = (self.terminal_length, self.h // 2)
        t2_a = (self.w - self.terminal_length, self.h // 2)
        t2_b = (self.w, self.h // 2)

        painter.drawLine(*t1_a, *t1_b)
        painter.drawLine(*t2_a, *t2_b)

        painter.end()

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name

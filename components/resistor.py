from PyQt6.QtWidgets import (
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QWidget,
    QGraphicsItem,
    QGraphicsObject,
)
from PyQt6.QtGui import QPainter, QPen, QPainterPath, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QLineF, QObject
from components.draggable_component import DraggableComponent


class Resistor(QGraphicsItem):
    name = "Resistor"

    class Signals(QGraphicsObject):
        terminalClicked = pyqtSignal(str, int)
        componentMoved = pyqtSignal()

    def __init__(self, compCount: int, parent=None):
        super(Resistor, self).__init__(parent)
        self.uniqueID = f"{self.name}-{compCount}"

        self.signals = self.Signals()

        self.w = 70
        self.h = 20
        self.terminal_length = 15
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        self.hovered_terminal = None
        self.setAcceptHoverEvents(True)

        self.signals.componentMoved.connect(self.update)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        pos = event.pos()
        terminal_positions = self.getTerminalPositions()
        for terminal_position in terminal_positions:
            distance = QLineF(pos, self.mapFromScene(terminal_position)).length()
            if distance < float(5):
                self.hovered_terminal = self.mapFromScene(terminal_position)
                break
            else:
                self.hovered_terminal = None
        self.update()
        return super().hoverMoveEvent(event)

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

        # draw circle around the hovered terminal
        if self.hovered_terminal is not None:
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            radius = 5
            painter.drawEllipse(self.hovered_terminal, radius, radius)

    def getTerminalPositions(self):
        t1_pos = self.mapToScene(0, self.h // 2)
        t2_pos = self.mapToScene(self.w, self.h // 2)
        # t1_pos = QPointF(0, self.h // 2)
        # t2_pos = QPointF(self.w, self.h // 2)
        return t1_pos, t2_pos

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            terminal_positions = self.getTerminalPositions()
            clicked_terminal = None
            min_distance = float(5)

            for terminal_pos in terminal_positions:
                distance = QLineF(pos, terminal_pos).length()
                print(distance)
                if distance < min_distance:
                    min_distance = distance
                    clicked_terminal = terminal_pos

            if clicked_terminal is not None:
                terminal_index = terminal_positions.index(clicked_terminal)
                self.signals.terminalClicked.emit(self.uniqueID, terminal_index)
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.signals.componentMoved.emit()
        return super().mouseMoveEvent(event)

    def __str__(self) -> str:
        return "Resistor"

    def __repr__(self):
        return "Resistor"

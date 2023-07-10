import typing
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

GRID_SIZE = 40


class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gridPen = QtGui.QPen(QtGui.QColor(50, 50, 50))
        self.terminalPen = QtGui.QPen(QtGui.QColor(20, 255, 20), 5)
        # test terminals
        self.t1 = QtCore.QPointF(40, 40)
        self.t2 = QtCore.QPointF(320, 400)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Calculate the left, top, right, and bottom coordinates of the visible area
        left = int(rect.left()) - (int(rect.left()) % GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % GRID_SIZE)
        right = int(rect.right())
        bottom = int(rect.bottom())

        # Generate vertical grid lines
        lines = []
        for x in range(left, right, GRID_SIZE):
            lines.append(((x, top), (x, bottom)))

        # Generate horizontal grid lines
        for y in range(top, bottom, GRID_SIZE):
            lines.append(((left, y), (right, y)))

        # Set the pen for drawing the grid lines
        painter.setPen(self.gridPen)

        # Draw the grid lines
        for line in lines:
            start_point = line[0]
            end_point = line[1]
            painter.drawLine(*start_point, *end_point)

        # draw test terminals
        painter.setPen(self.terminalPen)
        painter.drawPoint(self.t1)
        painter.drawPoint(self.t2)


class Wire(QtWidgets.QGraphicsItem):
    def __init__(self, parent: QGraphicsItem | None = ...) -> None:
        super().__init__(parent)


class WireSegment(QtWidgets.QGraphicsItem):
    def __init__(self, start: QPointF = None, end: QPointF = None, parent=None):
        super().__init__(parent)
        self.start = start if start is not None else QPointF(40, 40)
        self.end = end if end is not None else QPointF(40, 200)

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setPen(QtGui.QPen(QColor(255, 20, 20), 1))
        painter.drawLine(self.start, self.end)

    def boundingRect(self) -> QRectF:
        return QRectF(self.start, self.end).normalized()


class View(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setGeometry(1100, 150, 600, 600)
        self.setScene(GridScene(self))
        # self.setBackgroundBrush(Qt.GlobalColor.black)

        self.setOptimizationFlag(
            QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True
        )
        # RubberBandDrag mode allows the selection of multiple components by dragging to draw a rectangle around them
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        start_point = QPointF(10, 10)
        end_point = QPointF(100, 100)
        wireSegment = WireSegment()
        self.scene().addItem(wireSegment)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = View()
    window.show()
    app.exec()

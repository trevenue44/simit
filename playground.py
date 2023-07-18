import typing
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent

import logging

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

    def getClosestTerminal(self, position: QtCore.QPoint):
        for t in (self.t1, self.t2):
            d = QtCore.QLineF(t, position.toPointF()).length()
            if d <= 5:
                return t
        return None


class Wire(QtWidgets.QGraphicsItem):
    def __init__(
        self, startTerminalPosition: QtCore.QPointF, parent: QGraphicsItem | None = None
    ) -> None:
        super().__init__(parent)
        self.refPoint = startTerminalPosition
        self.points = [startTerminalPosition]
        self.possibleNextPoint = None

    def addNewPoint(self, point: QtCore.QPointF):
        self.points.append(point)
        self.refPoint = self.points[-1]
        self.update()
        if self.scene():
            self.scene().update()

    def paint(self, painter: QPainter, option, widget):
        painter.setPen(QtGui.QPen(QColor(255, 20, 20), 2))
        for index in range(len(self.points) - 1):
            start = self.mapToScene(self.points[index])
            end = self.mapToScene(self.points[index + 1])
            painter.drawLine(start, end)

        if self.possibleNextPoint is not None:
            painter.drawLine(self.refPoint, self.mapToScene(self.possibleNextPoint))

    def boundingRect(self) -> QRectF:
        return QRectF()

    def shape(self) -> QtGui.QPainterPath:
        path = QtGui.QPainterPath()
        for index in range(len(self.points) - 1):
            start = self.mapToScene(self.points[index])
            end = self.mapToScene(self.points[index + 1])
            path.moveTo(start)
            path.lineTo(end)

        return path
    
    def contains(self, point: QtCore.QPointF) -> bool:
        return True

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        print("Wire Pressed")
        return super().mousePressEvent(event)


class View(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.scene: GridScene = GridScene(self)

        self.currentWire: Wire | None = None

        self.initUI()

    def initUI(self):
        self.setGeometry(1100, 150, 600, 600)
        self.setScene(self.scene)

        self.setOptimizationFlag(
            QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True
        )
        # RubberBandDrag mode allows the selection of multiple components by dragging to draw a rectangle around them
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        wire = Wire(QPointF(80, 80))
        wire.points.extend([QPointF(80, 160), QPointF(240, 160), QPointF(240, 200)])
        self.scene.addItem(wire)

    def normalizePointToGrid(self, p: QPointF) -> QPointF:
        x = round(p.x() / GRID_SIZE) * GRID_SIZE
        y = round(p.y() / GRID_SIZE) * GRID_SIZE
        return QPointF(x, y)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.currentWire is not None:
            print("before", self.currentWire.points)
            # currently drawing a wire.
            # we take the current point that the user has clicked on
            # and add that to the points list of the current wire
            # depending on whether the horizontal line is better or the vertical one is better.
            refPoint = self.currentWire.refPoint
            clickedPoint = self.normalizePointToGrid(event.pos().toPointF())

            if clickedPoint in self.currentWire.points:
                id = self.currentWire.points.index(clickedPoint)
                self.currentWire.points = self.currentWire.points[: id + 1]
                self.currentWire.refPoint = self.currentWire.points[-1]
            else:
                y_difference = abs(refPoint.y() - clickedPoint.y())
                x_difference = abs(refPoint.x() - clickedPoint.x())
                if x_difference > y_difference:
                    # vertical line is longer so we keep the y constant and change the x rahter
                    newPoint = QPointF(clickedPoint.x(), refPoint.y())
                else:
                    newPoint = QPointF(refPoint.x(), clickedPoint.y())
                self.currentWire.addNewPoint(newPoint)
            if self.currentWire in self.scene.items():
                self.scene.removeItem(self.currentWire)
            self.scene.addItem(self.currentWire)
            self.scene.update()
            print("after", self.currentWire.points)
        else:
            # if there's no currentWire, check if a terminal has been clicked.
            # If a terminal has been clicked, then start creating a new wire
            terminal = self.scene.getClosestTerminal(event.pos())
            if terminal is not None and self.currentWire is None:
                self.currentWire = Wire(startTerminalPosition=terminal)
                # self.scene.addItem(self.currentWire)
                # logging.info(f"created current wire, {self.currentWire}")
                logging.info(f"created current wire, {self.currentWire}")
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        return super().mouseMoveEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = View()
    window.show()
    app.exec()

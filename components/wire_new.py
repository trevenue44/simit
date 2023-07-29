import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor

import constants
from components.general import ComponentAndTerminalIndex


class Wire(QGraphicsItem):
    def __init__(self, start: ComponentAndTerminalIndex, parent=None) -> None:
        super().__init__(parent)
        self.setZValue(10)

        self._start = start
        self._end: ComponentAndTerminalIndex | None = None

        self._refPoint = start.component.getTerminalPositions()[start.terminalIndex]
        self._points = [self._refPoint]

        # connecting componentMoved signal from start component
        start.component.signals.componentMoved.connect(self._onStartComponentMoved)

    def setEnd(self, end: ComponentAndTerminalIndex):
        self._end = end
        end.component.signals.componentMoved.connect(self._onEndComponentMoved)

    def _onStartComponentMoved(self):
        newStartPos = self._start.component.getTerminalPositions()[
            self._start.terminalIndex
        ]
        self._points = self._points[::-1]
        self.addNewPoint(newStartPos)
        self._points = self._points[::-1]

    def _onEndComponentMoved(self):
        newEndPos = self._end.component.getTerminalPositions()[self._end.terminalIndex]
        self.addNewPoint(newEndPos)

    def addNewPoint(self, point: QPointF):
        # if point is already in _points, remove all other points after it to clear the wire after that point
        if point in self._points:
            id = self._points.index(point)
            self._points = self._points[: id + 1]
        else:
            dx = abs(self._refPoint.x() - point.x())
            dy = abs(self._refPoint.y() - point.y())
            if dx == 0:
                x = point.x()
                # get all the points on the vertical line
                y1 = int(self._refPoint.y())
                y2 = int(point.y())
                if y1 < y2:
                    step = constants.GRID_SIZE
                else:
                    step = -constants.GRID_SIZE
                for y in range(y1, y2 + step, step):
                    p = QPointF(x, y)
                    # if p is already in _points, remove every point up to p and continue from there
                    if p in self._points:
                        id = self._points.index(p)
                        self._points = self._points[:id]
                    self._points.append(p)
            elif dy == 0:
                y = point.y()
                # get all the points on the horizontal line according to grid
                x1 = int(self._refPoint.x())
                x2 = int(point.x())
                if x1 < x2:
                    step = constants.GRID_SIZE
                else:
                    step = -constants.GRID_SIZE
                for x in range(x1, x2 + step, step):
                    p = QPointF(x, y)
                    # if p is already in _points, remove every point up to p and continue from there
                    if p in self._points:
                        id = self._points.index(p)
                        self._points = self._points[:id]
                    self._points.append(p)
            else:
                # the line will have to be drawn in two parts. A horizontal one and a vertical one.
                # draw the longer one first.
                if dy > dx:
                    # vertical line is longer
                    # draw the vertical line first
                    # get the turning point
                    turningPoint = QPointF(self._refPoint.x(), point.y())
                else:
                    # horizontal line is longer or they are equal
                    # draw the horizontal line first
                    # get the turning point
                    turningPoint = QPointF(point.x(), self._refPoint.y())
                # add the turningPoint and clicked point to the points list in order
                self.addNewPoint(turningPoint)
            # add the point itself
            self._points.append(point)
        # update the reference point
        self._refPoint = self._points[-1]
        self.update()

    def getRefPoint(self) -> QPointF:
        return self._refPoint

    def setRefPoint(self, p: QPointF):
        id = self._points.index(p)
        self._points = self._points[: id + 1]
        self._refPoint = self._points[-1]

    def getPoints(self) -> list[QPointF]:
        return self._points

    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setPen(QPen(QColor(255, 20, 20), 2))

        # draw the lines between points
        for index in range(len(self._points) - 1):
            start = self.mapToScene(self._points[index])
            end = self.mapToScene(self._points[index + 1])
            painter.drawLine(start, end)

    def boundingRect(self):
        return QRectF()

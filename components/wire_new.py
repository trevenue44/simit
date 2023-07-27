import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor


class Wire(QGraphicsItem):
    def __init__(self, startPos: QPointF, parent=None) -> None:
        super().__init__(parent)
        self.setZValue(10)

        self._refPoint = startPos
        self._points = [startPos]

    def addNewPoint(self, point: QPointF):
        self._points.append(point)
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

        for index in range(len(self._points) - 1):
            start = self.mapToScene(self._points[index])
            end = self.mapFromScene(self._points[index + 1])
            painter.drawLine(start, end)

    def boundingRect(self):
        return QRectF()

from typing import List

from PyQt6 import QtCore
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsTextItem
from PyQt6.QtCore import QPointF, QRectF, Qt, QLineF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QPainterPathStroker

import constants
from components.general import ComponentAndTerminalIndex

import math

from SimulationBackend.middleware import CircuitNode


class Wire(QGraphicsItem):
    name = "Wire"

    def __init__(
        self, start: ComponentAndTerminalIndex, wireCount: int, parent=None
    ) -> None:
        super().__init__(parent)
        self.setZValue(1)

        # create uniqueID of wire
        self.uniqueID = f"{self.name}-{wireCount}"

        self._start = start
        self._end: ComponentAndTerminalIndex | None = None

        self._startPoint = self._refPoint = start.component.getTerminalPositions()[
            start.terminalIndex
        ]
        self._points = [self._refPoint]
        self._endPoint: QPointF | None = None

        # connecting componentMoved signal from start component
        start.component.signals.componentMoved.connect(self._onStartComponentMoved)

        # keeping track of the circuit node that a particular wire forms
        self.circuitNode: CircuitNode | None = None

        self.initUI()

    def initUI(self):
        # make the wire selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # initialise text item to write node labels and node voltages
        self.textItem = QGraphicsTextItem(self)
        self.textItem.setDefaultTextColor(Qt.GlobalColor.yellow)
        self.textItem.setFont(QFont("Arial", 10))
        self.textItem.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)

    def updateWireText(self):
        # write simulation results if there is some
        if self.circuitNode:
            # calculate the midpoint of the wire
            midpoint = self._points[len(self._points) // 2]

            text = f"CN-{self.circuitNode.uniqueID.split('-')[-1]}"

            if self.getNodeVoltage():
                # get node data
                # eg: ["10.00", "V"]
                nodeVoltage = self.getNodeVoltage()
                # combine value and unit into one text
                text = f"{text}\n{' '.join(nodeVoltage)}"

            # set text and initial position
            self.textItem.setPlainText(text)
            self.textItem.setPos(midpoint)

            # Adjust the position of the text item to center it horizontally
            textWidth = self.textItem.boundingRect().width()
            textHeight = self.textItem.boundingRect().height()
            self.textItem.setPos(
                midpoint.x() - textWidth / 2, midpoint.y() - textHeight / 2
            )

    def getNodeVoltage(self) -> List[str] | None:
        if self.circuitNode:
            return self.circuitNode.data.get("V")
        return None

    def setCircuitNode(self, circuitNode: CircuitNode) -> None:
        self.circuitNode = circuitNode
        self.circuitNode.signals.nodeDataChanged.connect(self.handleNodeDataChange)
        # write node ID on wire
        self.updateWireText()

    def handleNodeDataChange(self):
        self.updateWireText()

    def setEnd(self, end: ComponentAndTerminalIndex):
        self._end = end
        self._endPoint = end.component.getTerminalPositions()[end.terminalIndex]
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

    def paint(self, painter: QPainter, option, widget) -> None:
        if self.isSelected():
            pen = QPen(QColor(50, 205, 50), 3.5)
        else:
            pen = QPen(Qt.GlobalColor.darkGray, 2.5)

        painter.setPen(pen)
        painter.drawPath(self.path())

    def path(self) -> QPainterPath:
        """
        This method creates a QPainterPath that describes the shape of the wire.

        Returns:
            QPainterPath: A QPainterPath representing the shape of the wire.
        """
        path = QPainterPath()
        for i in range(len(self._points) - 1):
            path.moveTo(self._points[i])
            path.lineTo(self._points[i + 1])
        return path

    def boundingRect(self) -> QRectF:
        if self._points:
            return self.path().boundingRect()
        else:
            return QRectF()

    def shape(self):
        path = self.path()
        # Create a stroker to add allowance around the wire
        pen = QPen()
        # Set the width of the pen to determine the allowance
        pen.setWidth(5)
        stroker = QPainterPathStroker(pen)
        strokedPath = stroker.createStroke(path)

        return strokedPath

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        print("mouse pressseeeeedddddddd!!!")
        return super().mousePressEvent(event)

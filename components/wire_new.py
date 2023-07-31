from typing import List, Tuple, Union, Type

from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
    QGraphicsObject,
)
from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QPainterPathStroker

import constants
from components.general import ComponentAndTerminalIndex

from SimulationBackend.middleware import CircuitNode


class Wire(QGraphicsItem):
    name = "Wire"

    class Signals(QGraphicsObject):
        wireClicked = pyqtSignal(str, QPointF)
        wireSelected = pyqtSignal(str)
        wireDeselected = pyqtSignal(str)

    def __init__(
        self,
        start: ComponentAndTerminalIndex | Tuple[Union["Wire", QPointF]],
        wireCount: int,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setZValue(1)
        # create a signals class to keep track of signals
        self.signals = self.Signals()

        # create uniqueID of wire
        self.uniqueID = f"{self.name}-{wireCount}"

        if type(start) == ComponentAndTerminalIndex:
            self._startPoint = start.component.getTerminalPositions()[
                start.terminalIndex
            ]
            self._start = start
            # connecting componentMoved signal from start component
            start.component.signals.componentMoved.connect(self._onStartComponentMoved)
        elif type(start) == tuple:
            self._start: Wire = start[0]
            self._startPoint: QPointF = start[1]
        else:
            self._start: ComponentAndTerminalIndex | Wire | None = None

        self._end: ComponentAndTerminalIndex | Wire | None = None

        self._refPoint = self._startPoint
        self._points = [self._refPoint]
        self._endPoint: QPointF | None = None

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

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.signals.wireSelected.emit(self.uniqueID)
            else:
                self.signals.wireDeselected.emit(self.uniqueID)
            self.update()
        return super().itemChange(change, value)

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

    def setEnd(self, end: ComponentAndTerminalIndex | Tuple[Union["Wire", QPointF]]):
        if type(end) == ComponentAndTerminalIndex:
            self._end = end
            self._endPoint = end.component.getTerminalPositions()[end.terminalIndex]
            end.component.signals.componentMoved.connect(self._onEndComponentMoved)
        elif type(end) == tuple:
            self._end = end[0]
            self._endPoint = end[1]

    def _onStartComponentMoved(self):
        newStartPos = self._start.component.getTerminalPositions()[
            self._start.terminalIndex
        ]
        self._startPoint = newStartPos
        # get the end component and it's terminal
        startComponent = self._start.component
        componentTerminal = (startComponent.uniqueID, self._start.terminalIndex)
        if self._startPoint != self._points[0]:
            # component has been disconnected
            # remove component from node
            if self.circuitNode:
                if componentTerminal in self.circuitNode.componentTerminals:
                    self.circuitNode.componentTerminals.remove(componentTerminal)
        else:
            # component is still connected to the start
            if self.circuitNode:
                # only add the component back to the terminal list if it's not already there
                if componentTerminal not in self.circuitNode.componentTerminals:
                    self.circuitNode.componentTerminals.append(componentTerminal)

    def _onEndComponentMoved(self):
        newEndPos = self._end.component.getTerminalPositions()[self._end.terminalIndex]
        self._endPoint = newEndPos
        # get the end component and it's terminal
        endComponent = self._end.component
        componentTerminal = (endComponent.uniqueID, self._end.terminalIndex)
        if self._endPoint != self._points[-1]:
            # component has been disconnected
            # remove component from node
            if self.circuitNode:
                if componentTerminal in self.circuitNode.componentTerminals:
                    self.circuitNode.componentTerminals.remove(componentTerminal)
        else:
            # component is still connected to the end
            if self.circuitNode:
                # only add the component back to the terminal list if it's not already there
                if componentTerminal not in self.circuitNode.componentTerminals:
                    self.circuitNode.componentTerminals.append(componentTerminal)

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
            pen = QPen(QColor(50, 205, 50), 3)
        else:
            pen = QPen(Qt.GlobalColor.darkGray, 2)

        painter.setPen(pen)
        painter.drawPath(self.path())
        pen.setWidth(6)
        painter.setPen(pen)

        # draw a larger dot at the starting point if component is still connected to the start
        if self._startPoint == self._points[0]:
            painter.drawPoint(self._startPoint)

        # draw a larger dot at the ending point if component is still connected to the end
        if self._endPoint == self._points[-1]:
            painter.drawPoint(self._endPoint)

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
        # Capture the position of the mouse click
        clickedPoint = self.mapToScene(event.pos())

        # Initialize the minimum distance with a large value
        minDistance = float("inf")
        closestPoint = None

        # Calculate the distance to each point in _points
        for point in self._points:
            distance = (clickedPoint - point).manhattanLength()
            # If the calculated distance is smaller than the current minimum, update the minimum
            if distance < minDistance:
                minDistance = distance
                closestPoint = point

        # At this point, closestPoint is the point in _points closest to the clicked point
        # emit wire clicked signal with the wire ID and the point clicked
        self.signals.wireClicked.emit(self.uniqueID, closestPoint)

        return super().mousePressEvent(event)

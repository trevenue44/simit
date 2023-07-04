from typing import Tuple, Optional, List, Dict, Union

from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsObject,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)
from PyQt6.QtCore import pyqtSignal, QPointF, QLineF, Qt
from PyQt6.QtGui import QPainter, QPen, QFont

componentDataType = Dict[str, List[str]]
simulationResultsType = Dict[str, List[str]]


class GeneralComponent(QGraphicsItem):
    name: str = ...

    class Signals(QGraphicsObject):
        # signal sends (uniqueID, terminalIndex) as arguments.
        terminalClicked = pyqtSignal(str, int)
        componentMoved = pyqtSignal()
        componentSelected = pyqtSignal(str)
        componentDeselected = pyqtSignal(str)
        componentDataChanged = pyqtSignal()

    def __init__(self, compCount: int, parent=None) -> None:
        super(GeneralComponent, self).__init__(parent)
        # generate the uniqueID using the component name and the count.
        # eg. Resistor-23
        self.uniqueID = f"{self.name}-{compCount}"

        # geometry specifications of the component
        self.w: Union[float, int] = ...
        self.h: Union[float, int] = ...

        # component data attribute
        self.data: componentDataType = {}
        self.simulationResults: simulationResultsType = {}

        # a signals object attribute of the instance to send appropriate signals from different resistors
        self.signals = self.Signals()
        # update component text if data changes
        self.signals.componentDataChanged.connect(self.updateText)

        # Some flags of the QGraphicsItem
        # - Componenet draggable on scene
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # - Component selectable on scene
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Custom flags to help highlight terminal on hovered upon
        self.hoveredTerminal = None
        self.setAcceptHoverEvents(True)

        # initialize text item for displaying component information on component
        self.textItem = QGraphicsTextItem(self)
        self.textItem.setDefaultTextColor(Qt.GlobalColor.white)
        self.textItem.setFont(QFont("Arial", 8))

        # initialize component name and ID text item
        self.uniqueIDTextItem = QGraphicsTextItem(self)
        self.uniqueIDTextItem.setDefaultTextColor(Qt.GlobalColor.white)
        self.uniqueIDTextItem.setFont(QFont("Arial", 8))

        self.cnt = 0

    def initUI(self):
        self.writeUniqueID()

    def writeUniqueID(self):
        # write uniqueID under the component
        try:
            self.uniqueIDTextItem.setPlainText(self.uniqueID)
            self.uniqueIDTextItem.setPos(
                self.w / 2 - self.uniqueIDTextItem.boundingRect().width() / 2,
                self.boundingRect().height()
                - self.uniqueIDTextItem.boundingRect().height() / 2,
            )
        except Exception as e:
            print(f"[INFO] Unable to write uniqueID on component - Error: {e}")

    def setComponentData(self, key: str, value: List[str]):
        self.data[key] = value
        # emit data changed signals to trigger text update
        self.signals.componentDataChanged.emit()

    def setSimulationResults(self, key: str, value: List[str]):
        self.simulationResults[key] = value

    def updateText(self):
        ...

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.signals.componentSelected.emit(self.uniqueID)
            else:
                self.signals.componentDeselected.emit(self.uniqueID)
            self.update()
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option, widget) -> None:
        print(f"updating component {self.cnt}")
        self.cnt += 1
        # draw circle around the hovered terminal
        if self.hoveredTerminal is not None:
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            radius = 5
            painter.drawEllipse(self.hoveredTerminal, radius, radius)
        # draw a selection rectangle around the component when selected
        if self.isSelected():
            painter.setPen(QPen(Qt.GlobalColor.red, 0.3, Qt.PenStyle.DashLine))
            painter.drawRect(self.boundingRect())

    def getTerminalPositions(self) -> Tuple[QPointF, QPointF]:
        ...

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        pos = self.mapToScene(event.pos())
        hoveredTerminal = self.findClosestTerminal(pos)
        self.hoveredTerminal = (
            self.mapFromScene(hoveredTerminal) if hoveredTerminal else None
        )
        if hoveredTerminal is not None:
            self.update()
            ...
        return super().hoverMoveEvent(event)

    def findClosestTerminal(self, pos: QPointF) -> Optional[QPointF]:
        terminalPositions = self.getTerminalPositions()
        closestTerminal = None
        minDistance = float(5)

        for terminalPos in terminalPositions:
            distance = QLineF(pos, terminalPos).length()
            if distance <= minDistance:
                closestTerminal = terminalPos
                break
            elif distance - 5 <= minDistance:
                self.update()

        return closestTerminal

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            clickedTerminal = self.findClosestTerminal(pos)

            if clickedTerminal is not None:
                terminal_index = self.getTerminalPositions().index(clickedTerminal)
                self.signals.terminalClicked.emit(self.uniqueID, terminal_index)

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.signals.componentMoved.emit()
        return super().mouseMoveEvent(event)

    def rotate(self):
        newRotation = self.rotation() + 90
        self.setRotation(newRotation)

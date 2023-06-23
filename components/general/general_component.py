from typing import Tuple, Optional

from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)
from PyQt6.QtCore import pyqtSignal, QPointF, QLineF, Qt
from PyQt6.QtGui import QPainter, QPen


class GeneralComponent(QGraphicsItem):
    name: str = ...

    class Signals(QGraphicsObject):
        # signal sends (uniqueID, terminalIndex) as arguments.
        terminalClicked = pyqtSignal(str, int)
        componentMoved = pyqtSignal()

    def __init__(self, compCount: int, parent=None) -> None:
        super(GeneralComponent, self).__init__(parent)
        # generate the uniqueID using the component name and the count.
        # eg. Resistor-23
        self.uniqueID = f"{self.name}-{compCount}"

        # a signals object attribute of the instance to send appropriate signals from different resistors
        self.signals = self.Signals()

        # Some flags of the QGraphicsItem
        # - Componenet draggable on scene
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        # Custom flags to help highlight terminal on hovered upon
        self.hoveredTerminal = None
        self.setAcceptHoverEvents(True)

        # update the component whenever it is moved
        self.signals.componentMoved.connect(self.update)

    def paint(self, painter: QPainter, option, widget) -> None:
        # draw circle around the hovered terminal
        if self.hoveredTerminal is not None:
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            radius = 5
            painter.drawEllipse(self.hoveredTerminal, radius, radius)

    def getTerminalPositions(self) -> Tuple[QPointF, QPointF]:
        ...

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        pos = self.mapToScene(event.pos())
        hoveredTerminal = self.findClosestTerminal(pos)
        self.hoveredTerminal = (
            self.mapFromScene(hoveredTerminal) if hoveredTerminal else None
        )
        self.update()
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

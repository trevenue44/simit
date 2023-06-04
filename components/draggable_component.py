from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QWidget
from PyQt6 import QtGui


class DraggableComponent(QWidget):
    def __init__(self, parent=None):
        super(DraggableComponent, self).__init__(parent)

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.dragging:
            offset = event.pos() - self.dragStartPosition
            new_pos = self.pos() + offset
            self.move(new_pos)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

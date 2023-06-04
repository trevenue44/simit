from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QWidget
from PyQt6.QtGui import QColor, QCursor, QDrag
from PyQt6.QtCore import Qt, QPointF, Qt, QByteArray, QMimeData
from PyQt6 import QtGui


class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor(0, 0, 0))

    def add_component(self, component: QWidget):
        self.scene().addWidget(component())

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCore import QRectF, Qt, QPointF

from components.wire import Wire


class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.wire_tool_active = False
        self.selected_terminal_positions = []
        self.initUI()

    def initUI(self):
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(Qt.GlobalColor.black)

    def add_component(self, component: QGraphicsItem):
        comp = component()
        try:
            comp.terminalClicked.connect(self.onTerminalClick)
            print("terminal click signal connected")
        except Exception as e:
            ...
        self.scene().addItem(comp)

    def onWireToolClick(self, wire_tool_state: bool):
        self.wire_tool_active = wire_tool_state
        if not self.selected_terminal_positions:
            self.selected_terminal_positions = []

    def onTerminalClick(self, position: QPointF):
        print("terminal clicked")
        print("position", position)
        print(self.selected_terminal_positions)
        if self.wire_tool_active:
            if position in self.selected_terminal_positions:
                return
            self.selected_terminal_positions.append(position)

            if len(self.selected_terminal_positions) == 2:
                self.draw_wire()
                self.selected_terminal_positions = []

    def draw_wire(self):
        print("drawing wire")
        wire = Wire(
            self.selected_terminal_positions[0],
            self.selected_terminal_positions[1],
            # self.scene(),
        )
        self.scene().addItem(wire)
        print(self.selected_terminal_positions)

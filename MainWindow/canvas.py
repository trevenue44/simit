from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCore import QRectF, Qt, QPointF

from components.wire import Wire, ComponentAndTerminalIndex


class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.wire_tool_active = False
        self.selected_terminal_positions = []

        self.components = {}
        self.wires = {}

        self.initUI()

    def initUI(self):
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(Qt.GlobalColor.black)

    def add_component(self, component: QGraphicsItem):
        comp = component(compCount=len(self.components))
        try:
            comp.signals.terminalClicked.connect(self.onTerminalClick)
            print("terminal click signal connected")
        except Exception as e:
            ...
        self.scene().addItem(comp)
        self.components[comp.uniqueID] = comp

    def onWireToolClick(self, wire_tool_state: bool):
        self.wire_tool_active = wire_tool_state
        if not self.selected_terminal_positions:
            self.selected_terminal_positions = []

    def onTerminalClick(self, compID: str, terminal_index: int):
        print(f"terminal {terminal_index} of {compID} clicked!")
        print(self.selected_terminal_positions)
        if self.wire_tool_active:
            clicked_terminal = (compID, terminal_index)
            if clicked_terminal in self.selected_terminal_positions:
                print("terminal already in list")
                return
            self.selected_terminal_positions.append(clicked_terminal)

            if len(self.selected_terminal_positions) == 2:
                self.drawWire()
                self.selected_terminal_positions = []

        print("after terminal click:", self.selected_terminal_positions)

    def drawWire(self):
        print("drawing wire")
        start = ComponentAndTerminalIndex(
            self.components.get(self.selected_terminal_positions[0][0]),
            self.selected_terminal_positions[0][1],
        )
        end = ComponentAndTerminalIndex(
            self.components.get(self.selected_terminal_positions[1][0]),
            self.selected_terminal_positions[1][1],
        )
        wire = Wire(start, end)
        self.scene().addItem(wire)
        print("after_drawing: ", self.selected_terminal_positions)

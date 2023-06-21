from typing import Type
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt

from components.general import GeneralComponent
from components.wire import Wire, ComponentAndTerminalIndex


class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.wireToolActive = False
        self.selectedTerminals = []

        self.components = {}
        self.wires = {}

        self.initUI()

    def initUI(self):
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(Qt.GlobalColor.black)

    def addComponent(self, component: Type["GeneralComponent"]) -> None:
        comp = component(compCount=len(self.components))
        try:
            comp.signals.terminalClicked.connect(self.onTerminalClick)
            print("terminal click signal connected")
        except Exception as e:
            ...
        self.scene().addItem(comp)
        self.components[comp.uniqueID] = comp

    def onWireToolClick(self, wireToolState: bool):
        self.wireToolActive = wireToolState
        if not self.selectedTerminals:
            self.selectedTerminals = []

    def onTerminalClick(self, uniqueID: str, terminalIndex: int):
        print(f"terminal {terminalIndex} of {uniqueID} clicked!")
        print(self.selectedTerminals)
        if self.wireToolActive:
            clickedTerminal = (uniqueID, terminalIndex)
            if clickedTerminal in self.selectedTerminals:
                print("terminal already in list")
                return
            self.selectedTerminals.append(clickedTerminal)

            if len(self.selectedTerminals) == 2:
                self.drawWire()
                self.selectedTerminals = []

        print("after terminal click:", self.selectedTerminals)

    def drawWire(self):
        print("drawing wire")
        start = ComponentAndTerminalIndex(
            self.components.get(self.selectedTerminals[0][0]),
            self.selectedTerminals[0][1],
        )
        end = ComponentAndTerminalIndex(
            self.components.get(self.selectedTerminals[1][0]),
            self.selectedTerminals[1][1],
        )
        wire = Wire(start, end)
        self.scene().addItem(wire)
        print("after_drawing: ", self.selectedTerminals)

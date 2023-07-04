from typing import Type

from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QCursor
from PyQt6.sip import wrappertype

from utils.components import QHLine
from utils.functions import getComponentCategories
from components import COMPONENT_CATEGORY_MAPS
from components.general import GeneralComponent


class ComponentPane(QWidget):
    class Signals(QObject):
        componentSelected = pyqtSignal(wrappertype)

    def __init__(self, parent=None):
        super(ComponentPane, self).__init__(parent)

        # a signals object attribute of the instance to send appropriate signals from different resistors
        self.signals = self.Signals()

        self.initUI()

    def initUI(self):
        with open("./styles/components_pane.stylesheet.qss", "r") as f:
            styleSheet = f.read()
            self.setStyleSheet(styleSheet)
        self.setMinimumWidth(250)
        # virtical box layout to arrange components as a vertical list
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)

        # creating a search box to add to the top of the components list
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Search compnent")
        self.layout.addWidget(self.searchBox, alignment=Qt.AlignmentFlag.AlignTop)

        # adding a line separator between the search bar and the rest
        self.layout.addWidget(QHLine())

        # creating a dropdown menu used to select component category
        self.componentCategories = QComboBox()
        self.componentCategories.setPlaceholderText("Choose a component category")
        self.componentCategories.addItems(getComponentCategories())
        # self.componentCategories.setCurrentText("All")
        self.componentCategories.currentTextChanged.connect(
            self.onComponentCategoryChange
        )
        # self.onComponentCategoryChange()
        self.layout.addWidget(
            self.componentCategories, alignment=Qt.AlignmentFlag.AlignTop
        )

        # adding stretch to the bottom to push all the components up
        self.layout.addStretch()
        # using the vertical box layout as the layout of the component pane
        self.setLayout(self.layout)

    def onComponentCategoryChange(self):
        # get the selected category and the components in that category
        selectedCategory = self.componentCategories.currentText().strip()
        selectedCategoryComponents = COMPONENT_CATEGORY_MAPS.get(selectedCategory)

        # clear existing components from layout
        while self.layout.count() > 3:
            item = self.layout.takeAt(3)
            widget = item.widget()
            if widget is not None:
                self.layout.removeWidget(widget)
                widget.deleteLater()

        # add selected category components to the layout
        for component in selectedCategoryComponents:
            label = QLabel(component.name)
            label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            label.mousePressEvent = self.createComponentClickedHandler(component)
            self.layout.addWidget(label)

        # add stretch to the bottom to push all the components up
        self.layout.addStretch()

    def createComponentClickedHandler(self, component: Type["GeneralComponent"]):
        def handle_component_clicked(event):
            self.signals.componentSelected.emit(component)

        return handle_component_clicked

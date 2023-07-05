from typing import Type

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.sip import wrappertype

from utils.components import QHLine
from components.types import ComponentCategory
from components import getComponentClasses
from components.general import GeneralComponent


class ComponentsPane(QtWidgets.QWidget):
    class Signals(QtCore.QObject):
        componentSelected = QtCore.pyqtSignal(wrappertype)

    def __init__(self, parent=None):
        super(ComponentsPane, self).__init__(parent)

        # a signals object attribute of the instance to send appropriate signals from different resistors
        self.signals = self.Signals()
        # initial UI set up
        self.initUI()

    def initUI(self):
        with open("./styles/components_pane.stylesheet.qss", "r") as f:
            styleSheet = f.read()
            self.setStyleSheet(styleSheet)
        self.setMinimumWidth(250)

        # vertical box layout to arrange everything vertically
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)

        # add search box to the top of the components list
        self.searchBox = QtWidgets.QLineEdit()
        self.searchBox.setPlaceholderText("Search compnent or category")
        self.searchBox.textChanged.connect(self.onSearchBoxTextChange)
        self.layout.addWidget(self.searchBox)
        self.layout.setAlignment(self.searchBox, QtCore.Qt.AlignmentFlag.AlignTop)

        # add a line separtor between the search bar and the rest
        self.layout.addWidget(QHLine())

        # creating a dropdown menu used to select component category
        self.componentCategory = QtWidgets.QComboBox()
        self.componentCategory.setPlaceholderText("Choose a component category")
        categoryTexts = [category.value.capitalize() for category in ComponentCategory]
        categoryTexts.append("All")
        categoryTexts.sort()
        self.componentCategory.addItems(categoryTexts)
        self.componentCategory.currentTextChanged.connect(
            self.onComponentCategoryChange
        )

        # add drop down menu to the layout
        self.layout.addWidget(self.componentCategory)
        self.layout.setAlignment(
            self.componentCategory, QtCore.Qt.AlignmentFlag.AlignTop
        )

        # adding stretch to the bottom to push all the components up
        self.layout.addStretch()
        # using the vertical box layout as the layout of the component pane
        self.setLayout(self.layout)

    def clearComponents(self):
        while self.layout.count() > 3:
            item = self.layout.takeAt(3)
            widget = item.widget()
            if widget is not None:
                self.layout.removeWidget(widget)
                widget.deleteLater()

    def displayComponentClasses(self, componentClasses: list[Type["GeneralComponent"]]):
        for componentClass in componentClasses:
            label = QtWidgets.QLabel(componentClass.name)
            label.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            label.mousePressEvent = self.onComponentClassClick(componentClass)
            self.layout.addWidget(label)

    def onSearchBoxTextChange(self, searchText: str):
        self.clearComponents()
        componentClasses = getComponentClasses(searchText=searchText)
        # show components
        self.displayComponentClasses(componentClasses)
        # add stretch to the bottom to push all the components up
        self.layout.addStretch()

    def onComponentCategoryChange(self, text):
        # clear the current components
        self.clearComponents()
        # extract selected category
        if text.lower() == "all":
            componentClasses = getComponentClasses()
        else:
            selectedCategory = ComponentCategory[text.upper()]
            componentClasses = getComponentClasses(category=selectedCategory)
        # show components
        self.displayComponentClasses(componentClasses)

        # add stretch to the bottom to push all the components up
        self.layout.addStretch()

    def onComponentClassClick(self, component: Type["GeneralComponent"]):
        def onComponentClick(event):
            self.signals.componentSelected.emit(component)

        return onComponentClick

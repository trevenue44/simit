from typing import Type

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.sip import wrappertype

from utils.components import QHLine
from components.types import ComponentCategory
from components import getComponentClasses
from components.general import GeneralComponent


class ComponentsPane(QtWidgets.QWidget):
    class Signals(QtCore.QObject):
        """
        A Qbject class to organise all signals that would be emitted from the ComponentsPane
        """

        componentSelected = QtCore.pyqtSignal(wrappertype)

    def __init__(self, parent=None):
        super(ComponentsPane, self).__init__(parent)

        # a signals object attribute of the instance to send appropriate signals from different resistors
        self.signals = self.Signals()
        # initial UI set up
        self.initUI()

    def initUI(self):
        # load QSS stylesheet and set that as the stylesheet of the ComponentsPane
        with open("./styles/components_pane.stylesheet.qss", "r") as f:
            styleSheet = f.read()
            self.setStyleSheet(styleSheet)

        # making sure that the components pane is not any smaller than 250px
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
        # get a list of the category texts from the Component category enum that specifies the category a component belongs to
        categoryTexts = [category.value.capitalize() for category in ComponentCategory]
        categoryTexts.append("All")
        # sorting the categories to make sure they're in alphabetical order
        categoryTexts.sort()
        self.componentCategory.addItems(categoryTexts)
        # call the on component change function when the user changes the categry
        self.componentCategory.currentTextChanged.connect(
            self.onComponentCategoryChange
        )

        # add drop down menu to the layout
        self.layout.addWidget(self.componentCategory)
        self.layout.setAlignment(
            self.componentCategory, QtCore.Qt.AlignmentFlag.AlignTop
        )

        # sets the initial state of the components category to "All" to display all compnents from the start
        self.componentCategory.setCurrentText("All")

        # adding stretch to the bottom to push all the components up
        self.layout.addStretch()
        # using the vertical box layout as the layout of the component pane
        self.setLayout(self.layout)

    def clearComponents(self):
        """
        A utility function to clear every everything on the components pane except the first three i.e the searchbox, the line underneath it and the category combobox
        It's used to clear the listed components
        """
        while self.layout.count() > 3:
            item = self.layout.takeAt(3)
            widget = item.widget()
            if widget is not None:
                self.layout.removeWidget(widget)
                widget.deleteLater()

    def displayComponentClasses(self, componentClasses: list[Type["GeneralComponent"]]):
        """
        A function that takes in a list of the component classes to display and adds them to the layout
        """
        for componentClass in componentClasses:
            label = QtWidgets.QLabel(componentClass.name)
            label.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            label.mousePressEvent = self.onComponentClassClick(componentClass)
            self.layout.addWidget(label)

    def onSearchBoxTextChange(self, searchText: str):
        """
        A function that gets called whenever the text in the seach box changes.
        It clears the current components in there and uses the searchText to get the filtered component classes.
        It then calls the displayComponentClasses above to display the filtered component classes.
        It adds a stretch to make sure the components are all pushed up
        """
        self.clearComponents()
        componentClasses = getComponentClasses(searchText=searchText)
        # show components
        self.displayComponentClasses(componentClasses)
        # add stretch to the bottom to push all the components up
        self.layout.addStretch()

    def onComponentCategoryChange(self, text):
        """
        A function that gets called whenever category in the comboxbox is changed by the user.
        It clears the current components in there and uses the selected category to get the filtered component classes.
        It then calls the displayComponentClasses above to display the filtered component classes.
        It adds a stretch to make sure the components are all pushed up
        """
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
        """
        This function creates and returns the handler functions for each component that is displayed on components pane
        It handler function is customized based on component to make sure that the right component calsses are emitted when clicked on
        """

        def onComponentClick(event):
            self.signals.componentSelected.emit(component)

        return onComponentClick

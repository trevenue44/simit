from typing import Union, List

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QComboBox,
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QDoubleValidator, QCursor, QIcon

from components.general import GeneralComponent
from utils.components import QHLine


class AttributesPane(QWidget):
    class Signals(QObject):
        """
        A Qbject class to organise all signals that would be emitted from the Attributes pane
        """

        deleteComponent = pyqtSignal(str)

    def __init__(self, parent=None):
        super(AttributesPane, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # load QSS stylesheet and set that as the stylesheet of the attributes pane
        with open("./styles/attributes_pane.stylesheet.qss", "r") as f:
            styleSheet = f.read()
            self.setStyleSheet(styleSheet)

        # the attributes pane should not be smaller than 250 pixels.
        # makes the whole app look better
        self.setMinimumWidth(250)

        # vertical box layout to arrange everything vertically
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        # self.layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        # using the vertical box layout
        self.setLayout(self.layout)

        # creating an instance of the signals class above as an attribute of the AtrributesPane
        self.signals = self.Signals()

        # Keep track of the selected component; the component whose details would be displayed.
        self.selectedComponent: Union[GeneralComponent, None] = None

    def clearLayout(self, layout=None):
        """
        A utility function that applies recursion to clear the whole attributes pane

        The function goes through the contents of the layout and deletes all widgets.
        If it encounters a sub layout, it uses recursion to call itself on this layout and clear its inner widgets as well
        """
        if layout is None:
            layout = self.layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                layout.removeWidget(widget)
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if layout is not None:
                    self.clearLayout(sub_layout)

    def createPreviewComponent(self):
        """
        A function that creates and returns a clone of the selected component to be used in the preview section of the attributes pane.

        It gets the class of which the selected compnent is an instance of and creates a new instance of it.
        it then tweaks some flags to prevent the user from being able to select this preview component or move it around.
        It also makes sure that the preview component does not accept hover events in order to prevent unnessary re-rendering of the preview component.
        """
        previewComponent = type(self.selectedComponent)(compCount="X")
        previewComponent.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        previewComponent.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        previewComponent.setAcceptHoverEvents(False)
        return previewComponent

    def createPreviewSection(self) -> QVBoxLayout:
        """
        A function that creates and returns a layout containing the whole preview section of the attributes pane.

        It usese a vertical box layout to make sure everything is arranged vertically.
        It uses a label as the heading of the preview section.

        Underneath this, it adds a QGraphicsView with a QGraphicsScene that'd contain the preview component.
        A graphics scene is needed because the components are graphics itens.

        It calls the createPreviewComponent() above to get the preview component.

        It then sets some fixed dimensions of the preview graphics view and scene.
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        # heading of the preview section
        previewLabel = QLabel("Component Preview", self)
        previewLabel.setFont(QFont("Verdana", 15, 200))
        layout.addWidget(previewLabel)
        layout.setAlignment(previewLabel, Qt.AlignmentFlag.AlignTop)

        # creating a graphics view and scene to add the preview item to
        # create a graphics scene
        graphicsScene = QGraphicsScene(self)
        # create a graphics view
        graphicsView = QGraphicsView(graphicsScene)
        graphicsView.setBackgroundBrush(Qt.GlobalColor.black)
        # add the graphics view to the layout
        layout.addWidget(graphicsView)
        layout.setAlignment(graphicsView, Qt.AlignmentFlag.AlignTop)
        # create a preview instance of selected component
        self.previewComponent = self.createPreviewComponent()

        # add preview component to the scene
        graphicsScene.addItem(self.previewComponent)
        # set the scene rect to match the item size
        graphicsScene.setSceneRect(self.previewComponent.boundingRect())
        # set the fixed size of the view to match the scene's rect
        graphicsView.setFixedHeight(int(3 * graphicsScene.sceneRect().size().height()))
        return layout

    def createIDSection(self) -> QHBoxLayout:
        """
        This function creates and returns a layout containing the component ID section of the attributes pane.

        The ID section has the ID of the selected components and a delete button.
        It uses the horizontal box layout to make sure that they are side by side.
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # uniqueID label
        uniqueIDLabel = QLabel(self.selectedComponent.uniqueID, self)
        uniqueIDLabel.setFont(QFont("Verdana", 15))
        uniqueIDLabel.setMargin(0)
        layout.addWidget(uniqueIDLabel)

        # delete component button
        deleteButton = QPushButton("Delete", self)
        deleteButton.setFont(QFont("Verdana", 15))
        deleteButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        deleteButton.setStatusTip(f"Delete {self.selectedComponent.uniqueID}")
        deleteButton.setProperty("class", "delete-btn")
        deleteButton.setIcon(QIcon("./assets/bin-icon.png"))
        deleteButton.clicked.connect(self.onDeleteButtonClick)
        layout.addWidget(deleteButton)
        return layout

    def onDeleteButtonClick(self):
        """
        When the delete button on the ID sectinon is clicked,
        this function emits the deleteComponent signal which would be routed to a function on the canvas that deletes the selected component.
        The function also clears the attributes pane to make sure that selected compoent is still not being displayed even after deletion
        """
        self.signals.deleteComponent.emit(self.selectedComponent.uniqueID)
        self.clearLayout()

    def createAttributesSection(self) -> QVBoxLayout:
        """
        This function creates and returns a layout containing the actual attributes section of the attributes pane - where user can specify the attributes of selected component.

        It first makes a copy of the data coming in from the selected component.
        For each attribute in the component's data, it creates a horizontal box layout with the attribute's name, its value and its unit.
        It uses a QLineEdit for the attribute's value and a drop down for the unit, allowing the user to tweak the values inside the data attribute.

        It then combines all the HBoxLayouts for the attributes into a VBoxLayout that
        """
        # getting component data
        data = self.selectedComponent.data.copy()

        # creating the initial layout
        layout = QVBoxLayout()

        # create attributes heading if there are attributes
        if len(data):
            attributesHeading = QLabel("Attributes", self)
            attributesHeading.setFont(QFont("Verdana", 15))
            layout.addWidget(attributesHeading)

        # float validator
        # Create a QDoubleValidator
        floatValidator = QDoubleValidator()
        floatValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        floatValidator.setDecimals(4)

        # creating editable sections for each property
        for property, value in zip(data.keys(), data.values()):
            # property name, value and unit will be side by side
            subLayout = QHBoxLayout()

            # property name
            propertyLabel = QLabel(f"{property} =")
            propertyLabel.setFont(QFont("Verdana", 15))
            subLayout.addWidget(propertyLabel)

            # line input box to enable user edit value of property
            propertyInputBox = QLineEdit(value[0], self)
            propertyInputBox.setValidator(floatValidator)
            subLayout.addWidget(propertyInputBox)

            # using a drop down menu for property units
            propertyUnitDropDown = QComboBox(self)
            propertyUnitDropDown.addItems(self.getPropertyUnits(property))
            propertyUnitDropDown.setCurrentText(value[1])
            subLayout.addWidget(propertyUnitDropDown)

            # connecting signals to slots
            propertyChangeHandler = lambda: self.handlePropertyInputSubmit(
                property,
                [
                    propertyInputBox.text().strip(),
                    propertyUnitDropDown.currentText().strip(),
                ],
            )
            propertyInputBox.textChanged.connect(propertyChangeHandler)
            propertyUnitDropDown.currentTextChanged.connect(propertyChangeHandler)

            layout.addLayout(subLayout)

        simulationResults = self.selectedComponent.simulationResults.copy()
        # create attributes heading if there are attributes
        if len(simulationResults):
            simulationResultsHeading = QLabel("Simulation Results", self)
            simulationResultsHeading.setFont(QFont("Verdana", 15))
            layout.addWidget(simulationResultsHeading)

        for result, value in zip(simulationResults.keys(), simulationResults.values()):
            subLayout = QHBoxLayout()

            # result label
            resultLabel = QLabel(f"{result} =", self)
            resultLabel.setFont(QFont("Verdana", 15))
            subLayout.addWidget(resultLabel)

            # an inactive lineinput box to enable user edit value of property
            resultValue = QLineEdit(value[0], self)
            resultValue.setDisabled(True)
            subLayout.addWidget(resultValue)

            # using QLabel for results unit
            resultUnit = QLabel(f"{value[1]}", self)
            subLayout.addWidget(resultUnit)

            layout.addLayout(subLayout)

        return layout

    def getPropertyUnits(self, property: str) -> List[str]:
        """
        A utility function that takes in a particular property of the component and returns a list of all the units available for the user to use.
        """
        if property == "V":
            return ["V", "kV"]
        if property == "R":
            return ["Ohm", "kOhm"]

    def handlePropertyInputSubmit(self, property: str, value: List[str]):
        """
        This function takes the current value and unit of a property on the attributes section whenever there's a change.
        It sets the new values as the componenets updated data. It also updates the components data for the preview componet too to make them sync.
        """
        if value[0]:
            value[0] = f"{float(value[0]):.2f}"
        else:
            value[0] = f"{0:.2f}"
        self.selectedComponent.setComponentData(property, value)
        self.previewComponent.setComponentData(property, value)

    def componentDeselected(self):
        """
        This is a slot to handle component deselection on the canvas.
        It clears the layout of the attributes pane and sets the selected component back to None.
        """
        self.clearLayout()
        self.selectedComponent = None

    def onCanvasComponentSelect(self, selectedComponent: GeneralComponent):
        """
        This is the slot that handles what happens on the attributes pane when a component is selected on the canvas.

        It takes in the selected components and first sets it as an attribute of the AtrributesPane.
        It then connects the component deselected signal to the slot that handles component deselection.
        It clears the layout in case any previous components were selected.
        It creates the various sections of the attributes pane and add them all to the main layout of the attributes pane in the right order.
        It finally adds a stretch at the bottom to make sure that everything is aligned and shifted to the top.
        """
        # set selected component
        self.selectedComponent = selectedComponent

        # connect component deselected signal
        self.selectedComponent.signals.componentDeselected.connect(
            self.componentDeselected
        )

        # clear current content of the attributes pane
        self.clearLayout()

        # create the preview section
        previewSection = self.createPreviewSection()
        self.layout.addLayout(previewSection)
        self.layout.setAlignment(previewSection, Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(QHLine())

        # create the ID section
        IDSection = self.createIDSection()
        self.layout.addLayout(IDSection)
        self.layout.setAlignment(IDSection, Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(QHLine())

        # create attributes section
        attributesSection = self.createAttributesSection()
        self.layout.addLayout(attributesSection)
        self.layout.setAlignment(attributesSection, Qt.AlignmentFlag.AlignTop)

        # adding stretch to the bottom to push all components up
        self.layout.addStretch()

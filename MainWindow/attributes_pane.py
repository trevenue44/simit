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
        deleteComponent = pyqtSignal(str)

    def __init__(self, parent=None):
        super(AttributesPane, self).__init__(parent)
        self.initUI()

    def initUI(self):
        with open("./styles/attributes_pane.stylesheet.qss", "r") as f:
            styleSheet = f.read()
            self.setStyleSheet(styleSheet)
        self.setMinimumWidth(250)

        # vertical box layout to arrange everything vertically
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        # self.layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        # using the vertical box layout
        self.setLayout(self.layout)

        # signals
        self.signals = self.Signals()

        # selected component
        self.selectedComponent: Union[GeneralComponent, None] = None

    def clearLayout(self, layout=None):
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
        previewComponent = type(self.selectedComponent)(compCount="X")
        previewComponent.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        previewComponent.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        previewComponent.setAcceptHoverEvents(False)
        return previewComponent

    def createPreviewSection(self):
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
        previewComponent = self.createPreviewComponent()

        # add preview component to the scene
        graphicsScene.addItem(previewComponent)
        # set the scene rect to match the item size
        graphicsScene.setSceneRect(previewComponent.boundingRect())
        # set the fixed size of the view to match the scene's rect
        graphicsView.setFixedHeight(int(3 * graphicsScene.sceneRect().size().height()))
        return layout

    def createIDSection(self):
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
        self.signals.deleteComponent.emit(self.selectedComponent.uniqueID)
        self.clearLayout()

    def createAttributesSection(self):
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
        if property == "V":
            return ["V", "kV"]
        if property == "R":
            return ["Ohm", "kOhm"]

    def handlePropertyInputSubmit(self, property: str, value: List[str]):
        if value[0]:
            value[0] = f"{float(value[0]):.2f}"
        else:
            value[0] = f"{0:.2f}"
        self.selectedComponent.setComponentData(property, value)

    def componentDeselected(self):
        self.clearLayout()
        self.selectedComponent = None

    def onCanvasComponentSelect(self, selectedComponent: GeneralComponent):
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

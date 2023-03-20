from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt
from utils.components import QHLine
from utils.functions import get_component_categories
from components import COMPONENT_CATEGORY_MAPS


class ComponentPane(QWidget):
    def __init__(self, parent=None):
        super(ComponentPane, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # virtical box layout to arrange components as a vertical list
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # creating a search box to add to the top of the components list
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search compnent")
        self.layout.addWidget(self.search_box, alignment=Qt.AlignmentFlag.AlignTop)

        # adding a line separator between the search bar and the rest
        self.layout.addWidget(QHLine())

        # creating a dropdown menu used to select component category
        self.component_categories = QComboBox()
        self.component_categories.setPlaceholderText("Choose a component category")
        self.component_categories.addItems(get_component_categories())
        self.component_categories.currentTextChanged.connect(
            self.on_component_category_change
        )
        self.layout.addWidget(
            self.component_categories, alignment=Qt.AlignmentFlag.AlignTop
        )

        # adding stretch to the bottom to push all the components up
        self.layout.addStretch()
        # using the vertical box layout as the layout of the component pane
        self.setLayout(self.layout)

    def on_component_category_change(self):
        selected_category = self.component_categories.currentText().strip()
        selected_category_components = COMPONENT_CATEGORY_MAPS.get(selected_category)
        for component in selected_category_components:
            self.layout.addWidget(QLabel(component))


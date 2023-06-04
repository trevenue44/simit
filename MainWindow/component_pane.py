from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.sip import wrappertype

from utils.components import QHLine
from utils.functions import get_component_categories
from components import COMPONENT_CATEGORY_MAPS


class ComponentPane(QWidget):
    component_selected = pyqtSignal(wrappertype)

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
        # get the selected category and the components in that category
        selected_category = self.component_categories.currentText().strip()
        selected_category_components = COMPONENT_CATEGORY_MAPS.get(selected_category)

        # clear existing components from layout
        while self.layout.count() > 3:
            item = self.layout.takeAt(3)
            widget = item.widget()
            if widget is not None:
                self.layout.removeWidget(widget)
                widget.deleteLater()

        # add selected category components to the layout
        for component in selected_category_components:
            label = QLabel(component.name)
            label.mousePressEvent = self.create_component_clicked_handler(component)
            self.layout.addWidget(label)

        # add stretch to the bottom to push all the components up
        self.layout.addStretch()

    def create_component_clicked_handler(self, component: QWidget):
        def handle_component_clicked(event):
            self.component_selected.emit(component)

        return handle_component_clicked

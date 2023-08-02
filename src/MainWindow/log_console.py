from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt


class LogConsole(QWidget):
    def __init__(self, parent=None):
        super(LogConsole, self).__init__(parent=parent)
        self._init_ui()

    def _init_ui(self):
        # load QSS stylesheet and set that as the stylesheet of the log console
        with open("src/styles/log_console.stylesheet.qss", "r") as f:
            styleSheet = f.read()
            self.setStyleSheet(styleSheet)

        # set the fixed height of the log console
        self.setFixedHeight(250)

        # create the layout of the log console
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # create the heading and add it to the layout
        self.heading = self._create_heading()
        self.layout.addWidget(self.heading)

        # create the text edit and add it to the layout
        self.text = self._create_text_edit()
        self.layout.addWidget(self.text)

        # set the layout of the log console
        self.setLayout(self.layout)

    def _create_heading(self):
        """Create a heading for the log console"""
        heading = QLabel("Log Console", self)
        heading.setFont(QFont("Verdana", 15))
        return heading

    def _create_text_edit(self):
        """Create a text edit widget to display the log messages"""
        text = QTextEdit()
        text.setReadOnly(True)
        text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        text.setFont(QFont("Arial", 10))
        text.setTextColor(Qt.GlobalColor.gray)
        text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return text

    def on_log(self, msg: str):
        """Slot to handle the log signal from the QtLogHandler"""
        self.text.append(msg)
        self._move_cursor_to_end()

    def _move_cursor_to_end(self):
        """Move the cursor of the QTextEdit to the end of the last line"""
        # Create a QTextCursor with the document of the QTextEdit
        text_cursor = QTextCursor(self.text.document())

        # Move the QTextCursor to the start of the last block (last line)
        text_cursor.movePosition(QTextCursor.MoveOperation.End)
        text_cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)

        # Set the QTextCursor of the QTextEdit
        self.text.setTextCursor(text_cursor)

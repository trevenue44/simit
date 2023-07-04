from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    with open("./styles/app.stylesheet.qss", "r") as f:
        styles = f.read()
        app.setStyleSheet(styles)
    app.exec()

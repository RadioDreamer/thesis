# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QAction,
    QIcon,
    QPixmap
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStyle,
    QLabel,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Membránrendszer szimuláció")

        # PLACEHOLDER!
        placeholder = QLabel("placeholder")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)
        #
        menu = self.menuBar()

        save_action = QAction("Mentés", self)
        load_action = QAction("Betöltés", self)
        load_structure = QAction("Membránstruktúra megadása", self)
        # Fájl menü
        file_menu = menu.addMenu("Fájl")
        file_menu.addActions([save_action,load_action,load_structure])

        # Futtatáshoz tartozó menü
        run_menu = menu.addMenu("Futtatás")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

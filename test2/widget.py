import sys

from PySide6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Membránrendszer szimuláció")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

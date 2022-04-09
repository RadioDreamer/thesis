import random
import sys

sys.path.append("../model")
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QGraphicsView, QGraphicsScene, QLabel,
    QWidget, QGraphicsItem, QGraphicsRectItem,
    QGraphicsSimpleTextItem, QPushButton, QVBoxLayout, QStatusBar, QDialog,
    QLineEdit, QDialogButtonBox, QMessageBox
)

from PySide6.QtGui import QResizeEvent, QAction
from StructureDialog import StructureDialog
from MembraneSimulator import MembraneSimulator, ModelType


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)
        self.setWindowTitle("Membránrendszer szimuláció")
        container = QWidget()
        self.setCentralWidget(container)
        self.membranes = MembraneSimulator(self.rect().width() / 2,
                                           self.rect().height() / 2)
        menu = self.menuBar()

        save_action = QAction("Mentés", self)
        load_action = QAction("Betöltés", self)

        # Fájl menü
        file_menu = menu.addMenu("Fájl")
        file_menu.addActions([save_action, load_action])

        # Struktúra megadásához menü
        create_menu = menu.addMenu("Membránstruktúra megadása")
        create_base_action = QAction("Alapmodell megadása", self)
        create_symport_action = QAction("Szimport/Antiport modell megadása",
                                        self)
        create_menu.addActions([create_base_action, create_symport_action])

        create_base_action.triggered.connect(self.create_base_dialog)
        create_symport_action.triggered.connect(self.create_symport_dialog)

        # Futtatáshoz tartozó menü
        run_menu = menu.addMenu("Futtatás")
        run_step = QAction("Szimuláció lépés futtatása", self)
        run_sim = QAction("Teljes szimuláció indítása", self)
        run_menu.addActions([run_sim, run_step])
        run_step.triggered.connect(self.membranes.simulate_step)
        run_sim.triggered.connect(self.membranes.simulate_computation)

        self.setStatusBar(QStatusBar(self))
        self.statusBar().addPermanentWidget(
            QPushButton("Teljes szimuláció indítása"))
        self.statusBar().addPermanentWidget(
            QPushButton("Szimuláció lépés indítása"))
        self.statusBar().addPermanentWidget(QLabel("Lépések száma: 0"))
        self.statusBar().hide()

        self.button = QPushButton("Press me")
        self.button.pressed.connect(self.btn_pressed)
        layout = QVBoxLayout()
        layout.addWidget(self.button)

        #        region = MyText(0, QRectF(0, 0, 100, 100), "Hello World")
        #        child_region = MyText(1, QRectF(0, 0, 50, 50), "Child", region)
        #        child_region2 = MyText(2, QRectF(0, 0, 30, 30), "Child2", region)

        #        self.membranes.regions[0] = region
        #        self.membranes.regions[1] = child_region
        #        self.membranes.regions[2] = child_region2

        layout.addWidget(self.membranes.view)
        # self.membranes.show_scene()
        container.setLayout(layout)

    def btn_pressed(self):
        if self.membranes.is_visible():
            self.membranes.hide_membranes()
        else:
            self.membranes.show_membranes()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        print("RESIZING", random.randint(0, 100))
        self.resize_scene()

    def resize_scene(self):
        if not self.isVisible():
            # Viewport size isn't set yet, so calculation won't work.
            return
        size = self.membranes.view.maximumViewportSize()
        self.membranes.view.scene().setSceneRect(0, 0, size.width(),
                                                 size.height())

    def create_base_dialog(self):
        dialog = StructureDialog(self, MembraneSimulator.is_valid_structure)
        dialog.exec()
        self.membranes.set_model(ModelType.BASE, dialog.get_text())
        self.statusBar().show()

    def create_symport_dialog(self):
        dialog = StructureDialog(self, MembraneSimulator.is_valid_structure)
        dialog.exec()
        self.membranes.set_model(ModelType.SYMPORT, dialog.get_text())
        self.statusBar().show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

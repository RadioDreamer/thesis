import random
import sys

sys.path.append("../model")
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QStatusBar,
    QFileDialog,
    QMessageBox
)

from PySide6.QtGui import QResizeEvent, QAction
from StructureDialog import StructureDialog
from MembraneSimulator import MembraneSimulator, ModelType
from HelpMenu import HelpMenu

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1400, 900)
        self.setWindowTitle("Membránrendszer szimuláció")
        # container = QWidget()

        self.membranes = MembraneSimulator(self.rect().width() / 2,
                                           self.rect().height() / 2)
        self.membranes.signal.counter_increment.connect(self.increment_counter_label)
        self.membranes.signal.simulation_over.connect(self.simulation_over)

        menu = self.menuBar()

        save_action = QAction("Mentés", self)
        save_action.setShortcut("Ctrl+S")
        load_action = QAction("Betöltés", self)
        load_action.setShortcut("Ctrl+O")

        # Fájl menü
        file_menu = menu.addMenu("Fájl")
        file_menu.addActions([save_action, load_action])

        # Struktúra megadásához menü
        create_menu = menu.addMenu("Membránstruktúra megadása")
        create_base_action = QAction("Alapmodell megadása", self)
        create_symport_action = QAction("Szimport/Antiport modell megadása",
                                        self)
        save_action.triggered.connect(self.save_file_dialog)
        load_action.triggered.connect(self.load_file_dialog)
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


        # Súgó
        help_menu = menu.addMenu("Súgó")
        help_action = QAction("Segítség a szoftver használatához", self)
        help_menu.addActions([help_action])
        help_action.triggered.connect(self.show_help)

        self.setStatusBar(QStatusBar(self))
        self.statusBar().addPermanentWidget(
            QPushButton("Teljes szimuláció indítása"))
        self.counter_label = QLabel("Lépések száma: 0")
        self.statusBar().addPermanentWidget(QPushButton("Szimuláció lépés indítása"))
        self.statusBar().addPermanentWidget(self.counter_label)
        self.statusBar().hide()

        self.setCentralWidget(self.membranes.view)
        # self.button = QPushButton("Press me")
        # self.button.pressed.connect(self.btn_pressed)
        # layout = QVBoxLayout()
        # layout.addWidget(self.button)
        #
        # layout.addWidget(self.membranes.view)
        # container.setLayout(layout)

    def increment_counter_label(self, event):
        self.counter_label.setText(str(event))

    def simulation_over(self, result):
        msg_box = QMessageBox()
        msg_box.setText(f"Simulation Over!\nResult:{result}")
        msg_box.exec()

    def show_help(self):
        help_menu = HelpMenu()
        help_menu.exec()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
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

    def save_file_dialog(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        self.membranes.save_model(name[0])

    def load_file_dialog(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        self.membranes.load_model(name[0])

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

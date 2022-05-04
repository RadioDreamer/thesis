import sys

sys.path.append("../model")
sys.path.append("../resources")

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QStatusBar,
    QFileDialog,
    QMessageBox,
    QDialog
)
from PySide6.QtCore import QFile
from PySide6.QtGui import QResizeEvent, QAction, QIcon

from StructureDialog import StructureDialog
from ModelType import ModelType
from MembraneSimulator import MembraneSimulator, InvalidStructureException
from HelpMenu import HelpMenu
from SimulationStepDialog import SimulationStepDialog
from ResultDialog import ResultDialog


class MainWindow(QMainWindow):
    """
    A class for displaying the main window of the application
    """

    def __init__(self):
        """
        The initializing function of the main window
        """

        super().__init__()
        # Size and title of the main window
        self.resize(1920, 1080)
        self.setWindowTitle("Membránrendszer szimuláció")

        # Instantiating the simulator widget and connect to it's signals
        self.membranes = MembraneSimulator(self.rect().width() / 2,
                                           self.rect().height() / 2)
        self.membranes.signal.counter_increment.connect(
            self.increment_counter_label)
        self.membranes.signal.simulation_over.connect(self.simulation_over)

        # Constructing the outer layer of the menubar
        menu = self.menuBar()
        save_action = QAction("Mentés", self)
        save_action.setShortcut("Ctrl+S")
        load_action = QAction("Betöltés", self)
        load_action.setShortcut("Ctrl+O")

        # File menu
        file_menu = menu.addMenu("Fájl")
        file_menu.addActions([save_action, load_action])

        # Menu for constructing the structure
        create_menu = menu.addMenu("Membránstruktúra megadása")
        create_base_action = QAction("Alapmodell megadása", self)
        create_symport_action = QAction("Szimport/Antiport modell megadása",
                                        self)

        # Connecting the signals
        save_action.triggered.connect(self.save_file_dialog)
        load_action.triggered.connect(self.load_file_dialog)
        create_menu.addActions([create_base_action, create_symport_action])
        create_base_action.triggered.connect(self.create_base_dialog)
        create_symport_action.triggered.connect(self.create_symport_dialog)

        # Menu for running the simulation
        run_menu = menu.addMenu("Futtatás")
        run_step = QAction("Szimuláció lépés futtatása", self)
        run_sim = QAction("Teljes szimuláció indítása", self)
        run_menu.addActions([run_sim, run_step])
        run_step.triggered.connect(self.membranes.simulate_step)
        run_sim.triggered.connect(self.run_simulation)

        # Help menu
        help_menu = menu.addMenu("Súgó")
        help_action = QAction("Segítség a szoftver használatához", self)
        help_menu.addActions([help_action])
        help_action.triggered.connect(self.show_help)

        # Constructing the statusbar
        self.setStatusBar(QStatusBar(self))
        run_sim_button = QPushButton("Teljes szimuláció indítása")
        run_step_button = QPushButton("Szimuláció lépés indítása")
        run_sim_button.clicked.connect(self.run_simulation)
        run_step_button.clicked.connect(self.membranes.simulate_step)

        self.statusBar().addPermanentWidget(run_sim_button)
        self.counter_label = QLabel("Lépések száma: 0")
        self.statusBar().addPermanentWidget(run_step_button)
        self.statusBar().addPermanentWidget(self.counter_label)
        self.statusBar().hide()

        self.setCentralWidget(self.membranes.view)

    def run_simulation(self):
        dialog = SimulationStepDialog()
        result = dialog.exec()
        if result == dialog.Accepted:
            self.membranes.simulate_computation(dialog.get_number())

    def increment_counter_label(self, event):
        """
        Event handler for incrementing the label which displays the number of
        steps the comptutation has gone through

        Parameters
        ----------
        event : int
            the new number of steps for the model
        """

        self.counter_label.setText(f"Lépések száma:{str(event)}")

    def simulation_over(self, result):
        """
        Event handler for the signal of the simulation ending

        Parameters
        ----------
        result : list
            the list containing the results
        """

        result_dialog = ResultDialog(result)
        result_dialog.exec()

    def show_help(self):
        """
        A function for instantiating and displaying the help menu for the user
        """

        help_menu = HelpMenu()
        help_menu.exec()

    def resizeEvent(self, event: QResizeEvent):
        """
        Event handler for resizing of the window

        Parameters
        ----------
        event : QResizeEvent
            the event containing information about the resizing
        """

        super().resizeEvent(event)
        self.resize_scene()

    def resize_scene(self):
        """
        A function that resizes the scene of the simulation
        """

        if self.membranes.model:
            size = self.membranes.view.maximumViewportSize()
            max_w = size.width()
            max_h = size.height()
            self.membranes.max_height = (3*max_h) / 4
            self.membranes.max_width = (3*max_w) / 4
            self.membranes.view.scene().setSceneRect(0, 0, max_w, max_h)
            self.membranes.draw_model()

    def create_base_dialog(self):
        """
        A function responsible for creating the dialog that is used to create a
        base model
        """

        dialog = StructureDialog(parent=self, type=ModelType.BASE, valid_fn=MembraneSimulator.is_valid_structure)
        result = dialog.exec()
        if result == QDialog.Accepted:
            try:
                self.membranes.set_model(ModelType.BASE, dialog.get_text())
                self.statusBar().show()
            except InvalidStructureException:
                msg_box = QMessageBox()
                msg_box.setText(
                    "A megadott szöveg formátuma helytelen!\nA súgó gombra "
                    "kattintva olvashatsz az elvárt formátumról.")
                msg_box.exec()

    def create_symport_dialog(self):
        """
        A function responsible for creating the dialog that is used to create a
        symport-antiport model
        """

        dialog = StructureDialog(parent=self,  type=ModelType.SYMPORT, valid_fn=MembraneSimulator.is_valid_structure)
        result = dialog.exec()
        if result == QDialog.Accepted:
            try:
                self.membranes.set_model(ModelType.SYMPORT, dialog.get_text())
                self.statusBar().show()
            except (InvalidStructureException, AssertionError):
                msg_box = QMessageBox()
                msg_box.setText(
                    "A megadott szöveg formátuma helytelen!\nA súgó gombra "
                    "kattintva olvashatsz az elvárt formátumról.")
                msg_box.exec()

    def save_file_dialog(self):
        """
        A function resposible for displaying the file saving dialog menu

        After selecting the file, the simulator object's `save_model()` will be
        called with the selected file path (if it is valid)
        """

        name = QFileDialog.getSaveFileName(self, 'Membránrendszer mentése fájlként')
        if name[0] != '':
            self.membranes.save_model(name[0])

    def load_file_dialog(self):
        """
        A function that displays the dialog used to load a membrane system in
        from a file

        After selecting the file, the simulator object's `load_model()` will be
        called with the selected file path (if the file truly exists)
        """

        name = QFileDialog.getOpenFileName(self, 'Membránrendszer betöltése', filter="JSON files (*.json)")
        if QFile.exists(name[0]):
            self.membranes.load_model(name[0])
            self.statusBar().show()


if __name__ == "__main__":
    app = QApplication([])

    # Setting up the application icon
    app.setWindowIcon(QIcon(":/icon/icon.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

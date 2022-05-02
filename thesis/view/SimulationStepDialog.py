from PySide6.QtWidgets import (
    QDialog,
    QSpinBox,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel
    )


class SimulationStepDialog(QDialog):
    """
    A class for displaying the dialog that is used to select the number of
    simulation steps to occur
    """

    def __init__(self, parent=None):
        """
        Initializing method for the dialog

        Parameters
        ----------
        parent : QWidget
            the parent widget of the dialog
        """

        super().__init__(parent)
        self.setWindowTitle("Szimulációk száma")
        self.label = QLabel("Add meg a szimulációk számát!")
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(1000)
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spin_box)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def get_number(self):
        """
        A getter method for returning the user input of the number of simulations

        Returns
        -------
        int
            the number the user selected
        """

        return self.spin_box.value()

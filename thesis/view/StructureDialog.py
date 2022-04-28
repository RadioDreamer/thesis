from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QMessageBox
)
from PySide6.QtGui import QFont
from MembraneSimulator import ModelType



class StructureDialog(QDialog):
    """
    A class for displaying the dialog that accepts the string representation of
    the membrane system's structure and objects

    Attributes
    ----------
    valid_fn : function
        the function that validates the structure from the user input
    _text : str
        the user input after clicking 'OK'
    button_box : QDialogButtonBox
        the button box to accept or the cancel the dialog
    layout : QVBoxLayout
        the layout of the dialog
    """

    def __init__(self, type=None, parent=None, valid_fn=None):
        """
        A function for initializing the dialog

        Parameters
        ----------
        parent : QWidget
            the parent widget of the dialog
        valid_fn : function
            the function that will be used to validate the user input
        """

        super().__init__(parent)
        self.setWindowTitle("Membránstruktúra megadása")
        self.valid_fn = valid_fn
        self.text = ""
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        if type == ModelType.BASE:
            msg = QLabel("Add meg az alapmodell struktúrájának szöveges reprezentációját!")
        elif type == ModelType.SYMPORT:
            msg = QLabel("Add meg a szimport-antiport rendszer struktúrájának szöveges reprezentációját!")

        font = QFont()
        font.setPointSize(11)
        msg.setFont(font)

        edit = QLineEdit()
        font.setPointSize(13)
        edit.setFont(font)

        edit.textChanged.connect(self.set_text)
        self.layout.addWidget(msg)
        self.layout.addWidget(edit)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def accept(self):
        """
        A slot connected to clicking the 'OK' button on the dialog

        If the user input is valid by `valid_fn`, then the base class's `accept`
        is called, else a `QMessageBox` appears with a warning
        """

        if self.valid_fn(self.text):
            super().accept()
        else:
            msg_box = QMessageBox()
            msg_box.setText("A megadott szöveg formátuma helytelen!\nA súgó gombra "
            "kattintva olvashatsz az elvárt formátumról.")
            msg_box.exec()

    def get_text(self):
        """
        A getter method for returning the user input

        Returns
        -------
        str
            the string containing the user input
        """

        return self.text

    def set_text(self, string):
        """
        A setter method for changing the variable that stores the user input

        Parameters
        ----------
        string : str
            the new value of the field `text`
        """

        self.text = string



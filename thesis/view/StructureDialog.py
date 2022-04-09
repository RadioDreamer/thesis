from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QMessageBox
)


class StructureDialog(QDialog):
    def __init__(self, parent=None, valid_fn=None):
        super().__init__(parent)
        self.setWindowTitle("Membránstruktúra megadása")
        self.valid_fn = valid_fn
        self.text = ""
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        msg = QLabel("Add meg a membránstruktúra szöveges reprezentációját!")
        edit = QLineEdit()

        edit.textChanged.connect(self.set_text)
        self.layout.addWidget(msg)
        self.layout.addWidget(edit)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def accept(self):
        if self.valid_fn(self.text):
            super().accept()
        else:
            msg_box = QMessageBox()
            msg_box.setText("Not a valid membrane system!")
            msg_box.exec()

    def set_text(self, string):
        self.text = string

    def get_text(self):
        return self.text

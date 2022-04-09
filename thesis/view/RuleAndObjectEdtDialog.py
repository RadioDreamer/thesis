from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QMessageBox
)


class RuleAndObjectEditDialog(QDialog):
    def __init__(self, region_objects, rules_string, type, valid_fn=None,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle("Régió szerkesztése")
        self.valid_fn = valid_fn
        self.rules = rules_string
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        obj_msg = QLabel("Add meg a régió új objektumait!")
        self.object_edit = QLineEdit()
        # self.object_edit.setPlaceholderText(region_objects)
        self.object_edit.setText(region_objects)

        rule_msg = QLabel("A régió jelenlegi szabályai!")
        self.rule_edit_list = QPlainTextEdit(self.rules)
        self.layout.addWidget(obj_msg)
        self.layout.addWidget(self.object_edit)
        self.layout.addWidget(rule_msg)
        self.layout.addWidget(self.rule_edit_list)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def get_rules(self):
        return self.rules

    def accept(self):
        if self.rules == self.rule_edit_list.toPlainText():
            super().accept()

        rule_list = self.rule_edit_list.toPlainText().split('\n')
        cond = True
        if rule_list != [""]:
            for rule in rule_list:
                if not self.valid_fn(rule):
                    cond = False
                    break

        if not cond:
            msg_box = QMessageBox(self)
            msg_box.setText("Nem helyes szabály!")
            msg_box.exec()
        else:
            self.rules = self.rule_edit_list.toPlainText()
            super().accept()

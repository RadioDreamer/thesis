import re

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
    """
    A class responsible for displaying the dialog for changing a region's
    rules and objects, then storing the input for updating the view

    Attributes
    ----------
    valid_fn : function
        the function that validates the rules from the user input
    rules : string
        the string containing the current rules of the region
    button_box : QDialogButtonBox
        the button box to accept or the cancel the dialog
    layout : QVBoxLayout
        the layout of the dialog
    object_edit : QLineEdit
        the editing tool for the objects in the region
    rule_edit_list : QPlainTextEdit
        the editor for editing the rules in the region
    """

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
        """
        Getter method for returning the state of the rules

        Returns
        -------
        str
            the string containing the state of the region's rules
        """

        return self.rules

    def accept(self):
        """
        Slot method for handling the user clicking the accept button

        If both the objects and the rules are valid, then calls the base
        class's `accept().
        """
        obj_cond = re.match(r'^[a-z]*$', self.object_edit.text()) is None

        rule_list = self.rule_edit_list.toPlainText().split('\n')
        all_rule_cond = True
        if rule_list != [""]:
            for rule in rule_list:
                if not self.valid_fn(rule):
                    all_rule_cond = False
                    break

        if not all_rule_cond or obj_cond:
            msg_box = QMessageBox(self)
            msg_box.setText("Nem helyes szabály!")
            msg_box.exec()
        else:
            self.rules = self.rule_edit_list.toPlainText()
            super().accept()

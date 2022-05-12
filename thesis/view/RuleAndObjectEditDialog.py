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
from PySide6.QtGui import QFont


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
        """
        The initializing method for the dialog

        Parameters
        ----------
        region_objects : str
            the string representation of the rules in the region
        rules_string : str
            the string representation of the rules in the region
        type : ModelType
            the type of the membrane system being edited
        valid_fn : function, optional
            the function used to validate the rules (default is None)
        parent : QWidget, optional
            the parent widget of the dialog (default is None)
        """
        super().__init__(parent)
        self.setWindowTitle("Régió szerkesztése")
        self.valid_fn = valid_fn
        self.rules = rules_string
        self.objects = region_objects

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        obj_msg = QLabel("Add meg a régió új objektumait!")
        self.object_edit = QLineEdit()
        self.object_edit.setText(region_objects)

        rule_msg = QLabel("A régió jelenlegi szabályai!")

        font = QFont()
        font.setPointSize(13)
        rule_msg.setFont(font)
        self.object_edit.setFont(font)

        self.rule_edit_list = QPlainTextEdit(self.rules)
        self.rule_edit_list.setFont(font)
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

    def reject(self):
        """
        Slot method for handling the user clicking the cancel button

        This means that the dialog's text fields have to be set back to the
        original state
        """

        self.object_edit.setText(self.objects)
        self.rule_edit_list.setPlainText(self.rules)
        super().reject()

    def accept(self):
        """
        Slot method for handling the user clicking the accept button

        If both the objects and the rules are valid, then calls the base
        class's `accept().
        """

        obj_cond = re.match(r'^[a-z]*$', self.object_edit.text()) is None

        rule_list = self.rule_edit_list.toPlainText().split('\n')
        rule_list = [r for r in rule_list if r != ""]
        all_rule_cond = True
        if rule_list:
            for rule in rule_list:
                if not self.valid_fn(rule):
                    all_rule_cond = False
                    break

        if not all_rule_cond or obj_cond:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Figyelmeztetés")
            msg_box.setText(
                "A megadott szabályok és objektumok közül (legalább az egyik) nem a helyes formátumú!")
            msg_box.exec()
        else:
            self.rules = '\n'.join(rule_list)
            super().accept()

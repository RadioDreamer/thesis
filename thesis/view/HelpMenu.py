from PySide6.QtWidgets import (
    QDialog,
    QTextBrowser,
    QVBoxLayout,
    QTextEdit,
    QDialogButtonBox
)

from PySide6.QtGui import QTextCursor, QTextBlockFormat
from help_script import HELP_TEXT

class HelpMenu(QDialog):
    """
    A class for displaying helpful information to the user using the simulator

    Attributes
    ----------
    button_box : QDialogButtonBox
        the button box to accept user input
    help_md : QTextEdit
        the text field for displaying the guide
    """

    def __init__(self, parent=None):
        """
        A function for initializing the guide

        The minimal size of the window is 750x400, in order to be readable

        Parameters
        ----------
        parent : QObject
            the parent of the dialog window
        """

        super().__init__(parent)
        self.setMinimumSize(750, 400)
        self.setWindowTitle("Használati útmutató")

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.setCenterButtons(True)

        # Original Markdown Layout
        self.help_md = QTextEdit(self)
        self.help_md.setReadOnly(True)
        self.help_md.resize(800, 800)
        self.help_md.setMarkdown('\n'.join(HELP_TEXT))

        # Scale the space between the lines
        block_fmt = QTextBlockFormat()
        block_fmt.setLineHeight(150, QTextBlockFormat.ProportionalHeight)
        cursor = self.help_md.textCursor()
        cursor.clearSelection()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_fmt)

        # Put the two widgets into a layout
        layout = QVBoxLayout()
        layout.addWidget(self.help_md)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

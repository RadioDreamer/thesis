from PySide6.QtWidgets import (
    QDialog,
    QTextBrowser,
    QVBoxLayout,
    QTextEdit,
    QDialogButtonBox
)

from PySide6.QtGui import QTextCursor, QTextBlockFormat


class HelpMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(750,400)

        with open("./software_guide.md") as md_file:
            help_md_string = md_file.readlines()

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.setCenterButtons(True)

        # Original Markdown Layout
        self.help_md = QTextEdit(self)
        self.help_md.setReadOnly(True)
        self.help_md.resize(800, 800)
        self.help_md.setMarkdown('\n'.join(help_md_string))

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



    def resizeEvent(self, event):
        self.help_md.resize(event.size())

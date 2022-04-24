from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QDialog,
    QDialogButtonBox
)


class ResultDialog(QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Szimulációs eredmények")
        self.layout = QVBoxLayout()

        self.inner_header_layout = QHBoxLayout()
        self.inner_header_layout.addWidget(QLabel("Számítási eredmények"))
        self.inner_header_layout.addWidget(QLabel("Gyakoriságok"))

        self.inner_data_layout = QHBoxLayout()
        self.data_list = QListWidget()

        sorted_by_freq = dict(sorted(results.items(), key=lambda x: x[0][1]))
        result_list = list(map(lambda x: str(x),sorted_by_freq.keys()))
        self.data_list.addItems(result_list)

        self.freq_list = QListWidget()
        freq_list = list(map(lambda x: str(x),sorted_by_freq.values()))
        self.freq_list.addItems(freq_list)

        self.inner_data_layout.addWidget(self.data_list)
        self.inner_data_layout.addWidget(self.freq_list)

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.setCenterButtons(True)


        self.layout.addLayout(self.inner_header_layout)
        self.layout.addLayout(self.inner_data_layout)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)


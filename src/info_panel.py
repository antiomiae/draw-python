from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

class InfoPanel(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self._text = ''
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.text_edit)
        self.layout().insertStretch(-1, 1)

        self.text_edit.setStyleSheet('QTextEdit { background: #444; color: #ccc }')

    def write_text(self, s: str):
        self._text += s.rstrip() + '\n'
        self.text_edit.setText(self._text)

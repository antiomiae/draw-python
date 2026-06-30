from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtCore import Qt

class OverlayWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

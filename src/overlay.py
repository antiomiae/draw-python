from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import Qt

class OverlayWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

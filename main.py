# This Python file uses the following encoding: utf-8
import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import Qt
from PySide2 import QtCore

from layer_view import LayerView

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, False)
    QApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, False)
    app = QApplication([])

    l = LayerView(size=QtCore.QSize(64, 64))
    l.show()

    sys.exit(app.exec_())

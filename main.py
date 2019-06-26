# This Python file uses the following encoding: utf-8
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QStyleFactory
from PySide2.QtCore import Qt
from PySide2 import QtCore

from draw_main_window import DrawMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, False)
    QApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, False)

    app = QApplication([])

    app.setStyle(QStyleFactory.create('windows'))

    QApplication.setOrganizationName('Kevin Ward')
    QApplication.setApplicationName('draw')

    l = DrawMainWindow()
    l.show()

    sys.exit(app.exec_())

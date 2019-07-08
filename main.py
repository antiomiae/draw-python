# This Python file uses the following encoding: utf-8
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QStyleFactory
from PySide2.QtCore import Qt
from PySide2 import QtCore

from draw_main_window import DrawMainWindow

import qtmodern.styles
import qtmodern.windows

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, False)
    QApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, False)

    app = QApplication([])


    # style_name = 'fusion'
    # if app.platformName() == 'windows':
    #     style_name = 'windows'
    # elif app.platformName() == 'cocoa':
    #     style_name = 'macos'

    # app.setStyle(QStyleFactory.create(style_name))

    QApplication.setOrganizationName('Kevin Ward')
    QApplication.setApplicationName('draw')

    qtmodern.styles.dark(app)

    main_window = DrawMainWindow()
    #main_window.show()

    modern_window = qtmodern.windows.ModernWindow(main_window)
    #
    modern_window.show()

    sys.exit(app.exec_())

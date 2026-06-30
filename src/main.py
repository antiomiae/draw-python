# This Python file uses the following encoding: utf-8
import sys
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from draw_main_window import DrawMainWindow

from qtmodernredux6 import QtModernRedux

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, False)
    QApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, False)

    app = QtModernRedux.QApplication([])

    # style_name = 'fusion'
    # if app.platformName() == 'windows':
    #     style_name = 'windows'
    # elif app.platformName() == 'cocoa':
    #     style_name = 'macos'

    # app.setStyle(QStyleFactory.create(style_name))

    QApplication.setOrganizationName("Kevin Ward")
    QApplication.setApplicationName("draw")

    main_window = DrawMainWindow()

    main_window.show()
    # modern_window = QtModernRedux.wrap(main_window)
    # #
    # modern_window.show()

    sys.exit(app.exec_())

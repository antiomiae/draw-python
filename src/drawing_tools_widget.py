from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


class DrawingToolsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QGridLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._pencil_button = self.create_tool_button(':/icons/draw_icons_pencil.png')
        self.layout().addWidget(self._pencil_button, 0, 0)

        self._eraser_button = self.create_tool_button(':/icons/draw_icons_eraser.png')
        self.layout().addWidget(self._eraser_button, 0, 1)

        self._selection_button = self.create_tool_button(':/icons/draw_icons_selection.png')
        self.layout().addWidget(self._selection_button, 1, 0)

        self._fill_button = self.create_tool_button(':/icons/draw_icons_bucket.png')
        self.layout().addWidget(self._fill_button, 1, 1)



    def create_tool_button(self, icon):
        button = QToolButton()
        button.setIcon(QIcon(icon))
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setIconSize(QSize(16, 16))

        return button

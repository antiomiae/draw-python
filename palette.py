from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore


class PaletteWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.palette = []
        self._width = 10
        self._height = 10
        self._item_size = QtCore.QSize(10, 10)

        self.setLayout(QtWidgets.QVBoxLayout())

        self.item_container = QtWidgets.QWidget()
        item_grid = QtWidgets.QGridLayout()
        self.item_container.setLayout(item_grid)

        item_grid.setSpacing(1)
        item_grid.setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(self.item_container)

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.item_container.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def set_palette(self, palette):
        self.palette = palette
        self.update_items()

    def update_items(self):
        layout = self.item_container.layout()

        for i, color in enumerate(self.palette):
            palette_item = PaletteItem(color, self._item_size)
            layout.addWidget(palette_item, i / self._height, i % self._width)

        for i in range(len(self.palette), self._width*self._height):
            palette_item = PaletteItem(QtGui.QColor(0, 0, 0, 50), self._item_size)
            layout.addWidget(palette_item, i / self._height, i % self._width)



class PaletteItem(QtWidgets.QWidget):
    def __init__(self, color=QtCore.Qt.GlobalColor.white, size=QtCore.QSize(10, 10)):
        super().__init__()
        self.color = color
        self.setMinimumSize(QtCore.QSize(10, 10))
        self.setMaximumSize(QtCore.QSize(10, 10))
        self._size = size
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setFixedSize(self._size)
        self.setContentsMargins(0, 0, 0, 0)

    def sizeHint(self):
        return self._size

    def minimumSizeHint(self):
        return self._size

    def paintEvent(self, event):
        cr = self.contentsRect()
        painter = QtGui.QPainter(self)
        painter.fillRect(cr, self.color)

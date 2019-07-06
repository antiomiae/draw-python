import sys

from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore

from draw_document import DrawDocument


class PaletteWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.palette = []
        self._width = 10
        self._height = 10
        self._item_size = QtCore.QSize(10, 10)
        self.toolbar = None

        self.setLayout(QtWidgets.QVBoxLayout())

        self.setup_toolbar()

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.layout().addWidget(self.scroll_area)

        self.item_container = QtWidgets.QWidget()
        self.item_container.setBackgroundRole(QtGui.QPalette.Window)

        self.scroll_area.setWidget(self.item_container)

        item_grid = QtWidgets.QGridLayout()
        item_grid.setSpacing(0)
        self.item_container.setLayout(item_grid)
        self.scroll_area.setFrameStyle(0)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setup_size_policies()
        self.restore_settings()

    def setup_size_policies(self):
        self.item_container.layout().setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

    def setup_toolbar(self):
        self.toolbar = QtWidgets.QToolBar(self)
        self.layout().insertWidget(0, self.toolbar)
        self.toolbar.setIconSize(QtCore.QSize(16, 16))
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.toolbar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

        enlarge_icon = QtGui.QIcon(':/icons/palette_icons_enlarge.png')
        shrink_icon = QtGui.QIcon(':/icons/palette_icons_shrink.png')
        delete_icon = QtGui.QIcon(':/icons/palette_icons_delete.png')
        add_icon = QtGui.QIcon(':/icons/palette_icons_add.png')

        add_action = self.toolbar.addAction(add_icon, 'add', self.handle_add)
        shrink_action = self.toolbar.addAction(shrink_icon, 'shrink palette', self.handle_shrink)
        enlarge_action = self.toolbar.addAction(enlarge_icon, 'enlarge palette', self.handle_enlarge)
        delete_action = self.toolbar.addAction(delete_icon, 'delete', self.handle_delete)

    def save_settings(self):
        settings = QtCore.QSettings()
        settings.setValue('editor/palette/item_size', self._item_size)

    def restore_settings(self):
        settings = QtCore.QSettings()
        self._item_size = settings.value('editor/palette/item_size', self._item_size)

    def handle_shrink(self):
        print('palette shrink')
        if self._item_size.width() > 8:
            self._item_size -= QtCore.QSize(1, 1)
        self.update_items()

    def handle_enlarge(self):
        print('palette enlarge')
        if self._item_size.width() < 64:
            self._item_size += QtCore.QSize(1, 1)
        self.update_items()

    def handle_delete(self):
        print('palette delete')

    def handle_add(self):
        print('palette add')
        if self.palette:
            pass
            # show color dialog

    def set_palette(self, palette):
        self.palette = palette
        self.update_items()

    def update_items(self):
        layout: QtWidgets.QGridLayout = self.item_container.layout()

        pool = [layout.takeAt(i).widget() for i in reversed(range(layout.count()))]

        for i, color in enumerate(self.palette):
            palette_item = (pool and pool.pop(-1)) or PaletteItem(size=self._item_size)
            palette_item.setFixedSize(self._item_size)
            layout.addWidget(palette_item, (i // self._width), (i % self._width))

            color = QtGui.QColor('#'+color) if color else None
            palette_item.color = color

        for leftover in pool:
            leftover.hide()
            leftover.deleteLater()

        self.item_container.updateGeometry()
        self.updateGeometry()
        self.parent().updateGeometry()

    @QtCore.Slot(DrawDocument)
    def document_changed(self, document):
        if document:
            self.set_palette(document.palette)


class PaletteItem(QtWidgets.QWidget):
    def __init__(self, *args, color=QtCore.Qt.GlobalColor.white, size=QtCore.QSize(10, 10)):
        super().__init__(*args)
        self._color = color
        #self.setMinimumSize(QtCore.QSize(10, 10))
        #self.setMaximumSize(QtCore.QSize(10, 10))
        self._size = size
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setFixedSize(self._size)
        self.setContentsMargins(0, 0, 0, 0)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self.update()

    def sizeHint(self):
        return self._size

    def minimumSizeHint(self):
        return self._size

    def paintEvent(self, event):
        cr = self.contentsRect()
        painter = QtGui.QPainter(self)
        if self.color:
            painter.fillRect(cr, self.color)
        else:
            painter.drawRect(self.rect())

        painter.end()

import os
import math

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtGui import QImage

from draw_document import DrawDocument


class DrawWindow(QtWidgets.QMdiSubWindow):
    MAX_ZOOM_LEVEL = 5
    MIN_ZOOM_LEVEL = -3

    def __init__(self, document = None):
        super().__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.document = document or DrawDocument()

        self.setWindowFilePath(self.document.file_path)
        self.setWindowTitle(self.document.name)

        self.canvas_size = self.document.size
        self._zoom_level = 0
        self.grid_spacing = 8
        self.show_grid = False

        self.window = QtWidgets.QMainWindow()

        self.setWidget(self.window)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)

        self.widget().setCentralWidget(self.scroll_area)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.window.setContentsMargins(0, 0, 0, 0)
        self.window.layout().setSpacing(0)
        self.window.layout().setContentsMargins(0, 0, 0, 0)

        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        self.canvas = CanvasLabel()
        self.scroll_area.setWidget(self.canvas)
        self.update_canvas()

        self.canvas.redraw.connect(self.on_canvas_redraw)

        self.setup_menus()

        self.render_document()

    def on_canvas_redraw(self, canvas):
        if self.show_grid:
            CanvasGrid.draw(canvas, self.canvas_size, 8, self.canvas_scale())

    def render_document(self):
        pixmap = QtGui.QPixmap(self.canvas_size)
        painter = QtGui.QPainter(pixmap)
        for layer in reversed(self.document.layers):
            if not layer.hidden:
                painter.drawImage(QtCore.QPoint(0, 0), layer.image)
        painter.end()
        self.canvas.setPixmap(pixmap)

    @property
    def zoom_level(self):
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, zoom):
        self._zoom_level = max(min(zoom, self.MAX_ZOOM_LEVEL), self.MIN_ZOOM_LEVEL)

    def canvas_scale(self):
        return math.pow(2, self.zoom_level)

    def canvas_transform(self) -> QtGui.QTransform:
        scale = self.canvas_scale()
        return QtGui.QTransform.fromScale(scale, scale)

    def update_canvas(self):
        new_size = self.canvas_size * self.canvas_scale()
        self.canvas.setFixedSize(new_size)

    def zoom_in(self):
        self.zoom_level += 0.5
        self.update_canvas()

    def zoom_out(self):
        self.zoom_level -= 0.5
        self.update_canvas()

    def toggle_grid(self, checked=False):
        self.show_grid = not self.show_grid
        self.canvas.update()

    def setup_menus(self):
        # toolbar_area = QtWidgets.QFrame()
        # self.widget().layout().insertWidget(0, toolbar_area)
        #
        # toolbar_area.show()
        # toolbar_area.setLayout(QtWidgets.QHBoxLayout())
        # toolbar_area.setBackgroundRole(QtGui.QPalette.Light)

        # toolbar = QtWidgets.QToolBar()
        toolbar = self.widget().addToolBar('bar')
        # toolbar_area.layout().addWidget(toolbar)

        toolbar.addAction('grid size')

        action = toolbar.addAction('Show grid')
        action.toggled.connect(self.toggle_grid)
        action.setCheckable(True)
        action.setChecked(self.show_grid)

        grid_size_input = QtWidgets.QSpinBox
        #grid_size_input.



class CanvasLabel(QtWidgets.QLabel):
    redraw = QtCore.Signal((QtCore.QObject,))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_overlay()
        self.setBackgroundRole(QtGui.QPalette.Light)
        self.setScaledContents(True)

    def setPixmap(self, pixmap):
        super().setPixmap(pixmap)
        if self.pixmap().size() != self.overlay_image.size():
            self.setup_overlay()

    def setup_overlay(self):
        size = None
        if self.pixmap():
            size = QtCore.QSize(self.pixmap().width(), self.pixmap().height())
        else:
            size = QtCore.QSize(self.size().width(), self.size().height())

        self.setup_overlay_image(size)

    def setup_overlay_image(self, size):
        self.overlay_image = QImage(size, QImage.Format_ARGB32_Premultiplied)
        self.overlay_image.setDevicePixelRatio(self.devicePixelRatioF())
        self.overlay_image.fill(QtGui.QColor(0, 0, 0, 0))

    def paintEvent(self, event):
        if self.pixmap():
            painter = QtGui.QPainter(self)
            self.drawFrame(painter)
            cr = self.contentsRect()
            painter.drawPixmap(cr, self.pixmap())
            painter.drawImage(cr, self.overlay_image)

            self.redraw.emit(self)

            painter.end()
        else:
            super().paintEvent(event)


class CanvasGrid:
    @staticmethod
    def draw(target, canvas_size, spacing, scale):
        painter = QtGui.QPainter(target)

        lines = []
        for x in range(spacing, canvas_size.width(), spacing):
            lines.append(QtCore.QLineF(x*scale, 0, x*scale, canvas_size.height()*scale))

        for y in range(spacing, canvas_size.height(), spacing):
            lines.append(QtCore.QLineF(0, y*scale, canvas_size.width()*scale, y*scale))

        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QtGui.QColor(128, 128, 128, 128))
        painter.setPen(pen)
        painter.drawLines(lines)

        painter.end()

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
        self.setStyle(QtWidgets.QStyleFactory.create('fusion'))

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
        self.scroll_area.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.window.setCentralWidget(self.scroll_area)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.window.layout().setSpacing(0)

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
        pixmap.fill(QtGui.QColor('transparent'))
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

    def _zoom(self, increment):
        viewport = self.scroll_area.viewport()
        cr = viewport.contentsRect()
        cr_center = cr.center()

        global_center = viewport.mapToGlobal(cr_center)
        p = self.canvas.mapFromGlobal(global_center)
        inverse_canvas_transform = self.canvas_transform().inverted()[0]
        pixel_position = inverse_canvas_transform.map(p)

        self.zoom_level += increment
        self.update_canvas()

        n = self.canvas_transform().map(pixel_position)

        h_scroll_bar = self.scroll_area.horizontalScrollBar()
        h_scroll_bar.setValue(float(pixel_position.x())/self.canvas_size.width()*h_scroll_bar.maximum())

        v_scroll_bar = self.scroll_area.verticalScrollBar()
        v_scroll_bar.setValue(float(pixel_position.y())/self.canvas_size.height()*v_scroll_bar.maximum())


    def zoom_in(self):
        self._zoom(0.5)

    def zoom_out(self):
        self._zoom(-0.5)

    def toggle_grid(self, checked=False):
        self.show_grid = not self.show_grid
        self.canvas.update()

    def setup_menus(self):
        pass
        # toolbar = self.widget().addToolBar('bar')
        #
        # toolbar.addAction('grid size')
        #
        # action = toolbar.addAction('Show grid')
        # action.toggled.connect(self.toggle_grid)
        # action.setCheckable(True)
        # action.setChecked(self.show_grid)
        #
        # grid_size_input = QtWidgets.QSpinBox()


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
        painter = QtGui.QPainter(self)
        self.drawFrame(painter)
        cr = self.contentsRect()

        bg_texture = QtGui.QPixmap()

        bg_texture.setDevicePixelRatio(self.devicePixelRatioF())
        bg_texture.load('bg_texture.png')
        bg_brush = QtGui.QBrush(bg_texture.scaled(bg_texture.size()*2))

        painter.fillRect(cr, bg_brush)

        painter.drawPixmap(cr, self.pixmap())
        painter.drawImage(cr, self.overlay_image)

        painter.end()

        self.redraw.emit(self)




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

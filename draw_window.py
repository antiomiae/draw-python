import os
import math

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtGui import QImage

from draw_document import DrawDocument


class DrawWindow(QtWidgets.QMdiSubWindow):
    MAX_ZOOM_LEVEL = 12
    MIN_ZOOM_LEVEL = -3

    def __init__(self, document = None):
        super().__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setStyleSheet('DrawWindow { '
                           'selection-background-color: blue; '
                           'selection-color: black;'
                           'color: green;'
                           'outline-color: red;'
                           'text-decoration: none;'
                           'alternate-background-color: yellow'
                           '}')

        self.document = document or DrawDocument()

        self.setWindowFilePath(self.document.file_path)

        self.canvas_size = self.document.size
        self._zoom_level = 0
        self.grid_spacing = 8
        self.show_grid = False

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scroll_area)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.canvas = CanvasLabel()
        self.scroll_area.setWidget(self.canvas)
        self.update_canvas()

        self.canvas.redraw.connect(self.on_canvas_redraw)

        self.setup_menus()

        self.render_document()
        self.update_title_bar_text()

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, document):
        self._document = document
        document.document_changed.connect(self.render_document)

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
        self.update_title_bar_text()

    def update_title_bar_text(self):
        self.setWindowTitle('{} ({:.2f}x)'.format(self.document.name, self.canvas_scale()))

    def canvas_scale(self):
        return math.pow(2, self.zoom_level)/self.devicePixelRatioF()

    def canvas_transform(self) -> QtGui.QTransform:
        scale = self.canvas_scale()
        return QtGui.QTransform.fromScale(scale, scale)

    def update_canvas(self):
        new_size = self.canvas_size * self.canvas_scale()
        self.canvas.setFixedSize(new_size)
        self.canvas.canvas_scale = self.canvas_scale()

    def _zoom(self, zoom):
        viewport = self.scroll_area.viewport()
        cr = viewport.contentsRect()
        cr_center = cr.center()

        global_center = viewport.mapToGlobal(cr_center)
        p = self.canvas.mapFromGlobal(global_center)
        inverse_canvas_transform = self.canvas_transform().inverted()[0]
        pixel_position = inverse_canvas_transform.map(p)

        self.zoom_level = zoom
        self.update_canvas()

        n = self.canvas_transform().map(pixel_position)

        h_scroll_bar = self.scroll_area.horizontalScrollBar()
        h_scroll_bar.setValue(float(pixel_position.x())/self.canvas_size.width()*h_scroll_bar.maximum())

        v_scroll_bar = self.scroll_area.verticalScrollBar()
        v_scroll_bar.setValue(float(pixel_position.y())/self.canvas_size.height()*v_scroll_bar.maximum())

    def zoom_in(self):
        self._zoom(self.zoom_level+0.5)

    def zoom_out(self):
        self._zoom(self.zoom_level-0.5)

    def reset_zoom(self):
        self._zoom(0)

    def toggle_grid(self, checked=False):
        self.show_grid = not self.show_grid
        self.canvas.update()

    def setup_menus(self):
        pass


class CanvasLabel(QtWidgets.QLabel):
    redraw = QtCore.Signal((QtCore.QObject,))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)

        self.canvas_scale = QtCore.QSizeF(1, 1)

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
        self.overlay_image = QImage(size, QImage.Format_ARGB32)
        self.overlay_image.setDevicePixelRatio(self.devicePixelRatioF())
        self.overlay_image.fill(QtGui.QColor(0, 0, 0, 0))

    def paintEvent(self, event):
        image_rect = QtCore.QRectF(QtCore.QPointF(0, 0), QtCore.QSizeF(self.pixmap().size())*self.canvas_scale)

        bg_texture = QtGui.QPixmap(':/textures/bg.png')
        bg_texture.setDevicePixelRatio(self.devicePixelRatioF())
        bg_brush = QtGui.QBrush(bg_texture)

        painter = QtGui.QPainter(self)
        painter.fillRect(self.contentsRect(), QtGui.QColor(0, 0, 0, 0))
        painter.fillRect(image_rect, bg_brush)
        painter.drawPixmap(image_rect, self.pixmap(), QtCore.QRectF(self.pixmap().rect()))
        painter.drawImage(image_rect, self.overlay_image)

        self.redraw.emit(self)
        painter.end()


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

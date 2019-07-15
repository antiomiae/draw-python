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

    __style_sheet = """
    DrawWindow { 
        selection-background-color: #888; 
        selection-color: black;
        color: #777;
        outline-color: red;
        text-decoration: none;
        alternate-background-color: yellow;
    }
    """

    def __init__(self, document = None):
        super().__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setStyleSheet(self.__style_sheet)

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
        self.canvas.redraw.connect(self.on_canvas_redraw)
        self.scroll_area.setWidget(self.canvas)
        self.update_canvas()

        self.setup_menus()

        self.render_document()
        self.update_title_bar_text()
        self.setWindowIcon(QtGui.QIcon(':/icons/emblem'))
        self.resize_contents(self.scroll_area.sizeHint())

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
        self.canvas.setPixmap(QtGui.QPixmap.fromImage(DocumentRenderer(self.document).render()))

    @property
    def zoom_level(self):
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, zoom):
        self._zoom_level = max(min(zoom, self.MAX_ZOOM_LEVEL), self.MIN_ZOOM_LEVEL)
        self.update_title_bar_text()

    def update_title_bar_text(self):
        self.setWindowTitle('{} ({:.2f}x)'.format(self.document.name, self.canvas_scale()*self.devicePixelRatioF()))

    def canvas_scale(self):
        return math.pow(2, self.zoom_level)/self.devicePixelRatioF()

    def canvas_transform(self) -> QtGui.QTransform:
        scale = self.canvas_scale()
        return QtGui.QTransform.fromScale(scale, scale)

    def update_canvas(self):
        new_size = self.canvas_size * self.canvas_scale()
        self.canvas.setFixedSize(new_size)
        self.canvas.resize(new_size)
        self.canvas.canvas_scale = self.canvas_scale()

    def _zoom(self, zoom):
        cr_center = self.scroll_area.contentsRect().center()
        global_center = self.scroll_area.mapToGlobal(cr_center)
        canvas_position = self.canvas.mapFromGlobal(global_center)
        inverse_canvas_transform = self.canvas_transform().inverted()[0]
        pixel_position = inverse_canvas_transform.map(QtCore.QPointF(canvas_position))

        self.zoom_level = zoom
        self.update_canvas()

        new_canvas_position = self.canvas_transform().map(pixel_position)
        self.center_canvas_at(new_canvas_position)

    def center_canvas_at(self, point):
        self.scroll_area.ensureVisible(point.x(), point.y(), self.scroll_area.width()/2, self.scroll_area.height()/2)

    def resize_contents(self, size):
        h = self.title_bar_height()
        w = self.frame_width()
        print('title bar height', h)
        print('frame width', w)
        self.resize(size + QtCore.QSize(w*2, h))

    def title_bar_height(self):
        style = self.style()
        so = QtWidgets.QStyleOptionTitleBar()
        so.titleBarState = 1
        so.titleBarFlags = QtCore.Qt.Window
        height = style.pixelMetric(QtWidgets.QStyle.PM_TitleBarHeight, so, self)
        return height + 4

    def frame_width(self):
        style = self.style()
        so = QtWidgets.QStyleOptionTitleBar()
        so.titleBarState = 1
        so.titleBarFlags = QtCore.Qt.Window
        width = style.pixelMetric(QtWidgets.QStyle.PM_MdiSubWindowFrameWidth, so, self)
        return width

    def zoom_in(self):
        self._zoom(self.zoom_level+0.25)

    def zoom_out(self):
        self._zoom(self.zoom_level-0.25)

    def reset_zoom(self):
        self._zoom(0)

    def toggle_grid(self, checked=False):
        self.show_grid = not self.show_grid
        self.canvas.update()

    def setup_menus(self):
        pass


class DocumentRenderer:
    def __init__(self, document):
        self.document = document
        self.painter = None

    def render(self):
        image = QtGui.QImage(self.document.size, QtGui.QImage.Format_ARGB32)
        self.painter = QtGui.QPainter(image)

        image.fill(QtGui.QColor('transparent'))

        for layer in reversed(self.document.layers):
            if not layer.hidden:
                self.set_blend_mode(layer)
                self.painter.drawImage(QtCore.QPoint(0, 0), layer.image)
        self.painter.end()

        return image

    def set_blend_mode(self, layer):
        if not layer.blend_mode or layer.blend_mode == 'normal':
            self.painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        else:
            self.painter.setCompositionMode(self.composition_mode_for_name(layer.blend_mode))

    def composition_mode_for_name(self, name):
        if name == 'darken':
            return QtGui.QPainter.CompositionMode_Darken
        if name == 'lighten':
            return QtGui.QPainter.CompositionMode_Lighten
        if name == 'add':
            return QtGui.QPainter.CompositionMode_Plus
        if name == 'difference':
            return QtGui.QPainter.CompositionMode_Difference
        if name == 'multiply':
            return QtGui.QPainter.CompositionMode_Multiply
        if name == 'screen':
            return QtGui.QPainter.CompositionMode_Screen
        if name == 'invert':
            return QtGui.QPainter.CompositionMode_Invert
        if name == 'overlay':
            return QtGui.QPainter.CompositionMode_Overlay
        if name == 'hardlight':
            return QtGui.QPainter.CompositionMode_HardLight
        if name == 'softlight':
            return QtGui.QPainter.CompositionMode_SoftLight
        if name == 'dodge':
            return QtGui.QPainter.CompositionMode_ColorDodge
        if name == 'burn':
            return QtGui.QPainter.CompositionMode_ColorBurn

        raise Exception('Unsupported composition mode \'%s\'' % name)

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

        self_rect = self.contentsRect()

        bg_texture = QtGui.QPixmap(':/textures/bg.png')
        bg_texture.setDevicePixelRatio(self.devicePixelRatioF())
        bg_brush = QtGui.QBrush(bg_texture)

        painter = QtGui.QPainter(self)
        painter.fillRect(self.contentsRect(), QtGui.QColor(0, 0, 0, 255))
        painter.fillRect(image_rect, bg_brush)
        painter.drawPixmap(image_rect, self.pixmap(), QtCore.QRectF(self.pixmap().rect()))
        #painter.drawImage(image_rect, self.overlay_image)
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

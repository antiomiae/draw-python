# utf-8
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtGui import QPainter, QImage, QPixmap

from inspect import getmembers
from dataclasses import dataclass

import math

import palette

class ImageLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setup_overlay()

    def resizeEvent(self, event):
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
        self.overlay_image.fill(QtGui.QColor(255, 0, 0, 128))

    def paintEvent(self, event):
        if self.pixmap():
            painter = QtGui.QPainter(self)
            self.drawFrame(painter)
            cr = self.contentsRect()
            painter.drawPixmap(cr, self.pixmap())

            painter.drawImage(cr, self.overlay_image)

            if self.window().show_grid:
                Grid.draw(self, self.window().grid_spacing)
        else:
            super().paintEvent(event)


class Grid:
    @staticmethod
    def draw(target, spacing):
        painter = QtGui.QPainter(target)
        cr = target.contentsRect()
        canvas_size = target.window().canvas_size
        scale = target.window().effective_canvas_scale()

        lines = []
        for x in range(spacing, canvas_size.width(), spacing):
            lines.append(QtCore.QLineF(x*scale, 0, x*scale, canvas_size.height()*scale))

        for y in range(spacing, canvas_size.height(), spacing):
            lines.append(QtCore.QLineF(0, y*scale, canvas_size.width()*scale, y*scale))

        pen = QtGui.QPen()
        pen.setWidth(0)
        pen.setColor(QtGui.QColor(0, 0, 0, 128))
        painter.setPen(pen)
        painter.drawLines(lines)


class LayerView(QtWidgets.QMainWindow):
    MAX_ZOOM_LEVEL = 5
    MIN_ZOOM_LEVEL = -3

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._zoom_level = 0
        self.grid_spacing = 8
        self.show_grid = False

        self.canvas_size = kwargs.get('size') or QtCore.QSize(256, 256)
        self.layer = Layer(self.canvas_size)
        self.tool = None

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.scroll_area)

        self.image_label = ImageLabel()
        self.image_label.setFrameRect(QtCore.QRect(0, 0, 0, 0))
        self.image_label.setFixedSize(self.canvas_size)
        self.image_label.setBackgroundRole(QtGui.QPalette.Light)
        self.scroll_area.setWidget(self.image_label)
        self.image_label.setScaledContents(True)

        self.draw_layer()

        self.setup_gestures()
        self.setup_actions()
        self.setup_docks()

        self.overlay = overlay.OverlayWidget(self.image_label)
        self.overlay.resize(self.image_label.size())
        self.overlay.show()

        p = QPainter(self.overlay)
        p.fillRect(self.overlay.rect(), QtCore.Qt.GlobalColor.black)

    def setup_gestures(self):
        self.grabGesture(QtCore.Qt.PinchGesture)

    def setup_actions(self):
        zoom_in_action = QtWidgets.QAction('Zoom In', self)
        zoom_in_action.setShortcut(QtGui.QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.handle_zoom_in)
        self.centralWidget().addAction(zoom_in_action)

        zoom_out_action = QtWidgets.QAction('Zoom Out', self)
        zoom_out_action.setShortcut(QtGui.QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.handle_zoom_out)
        self.centralWidget().addAction(zoom_out_action)

        toggle_grid_action = QtWidgets.QAction('Toggle Grid', self)
        toggle_grid_action.setShortcut(QtGui.QKeySequence.fromString('Ctrl+G'))
        toggle_grid_action.triggered.connect(self.handle_toggle_grid)
        self.centralWidget().addAction(toggle_grid_action)

    def setup_docks(self):
        dock = QtWidgets.QDockWidget('palette', self)

        self.palette_control = palette.PaletteWidget()
        self.palette_control.set_palette([QtCore.Qt.GlobalColor.white, QtCore.Qt.GlobalColor.black])
        dock.setWidget(self.palette_control)
        dock.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    @property
    def zoom_level(self):
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, zoom):
        self._zoom_level = max(min(zoom, self.MAX_ZOOM_LEVEL), self.MIN_ZOOM_LEVEL)

    def handle_zoom_in(self, checked):
        self.zoom_level += 0.5
        self.update_image_scale()

    def handle_zoom_out(self, checked):
        self.zoom_level -= 0.5
        self.update_image_scale()

    def handle_toggle_grid(self, checked):
        self.show_grid = not self.show_grid
        self.image_label.update()

    def effective_canvas_scale(self):
        return math.pow(2, self.zoom_level)

    def canvas_scale_matrix(self) -> QtGui.QTransform:
        scale = self.effective_canvas_scale()
        return QtGui.QTransform.fromScale(scale, scale)

    def draw_layer(self):
        self.image_label.setPixmap(QPixmap.fromImage(self.layer.image))
        self.update_image_scale()

    def update_image_scale(self):
        new_size = self.canvas_size*self.effective_canvas_scale()
        self.image_label.setFixedSize(new_size)

    def handle_gesture(self, event):
        event.accept()

    def line_complete(self, line):
        p = QPainter(self.layer.image)
        p.drawLine(QtCore.QLineF(line.start, line.end))
        p.end()
        self.tool = None
        self.draw_layer()

    def event(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.Gesture:
            return self.handle_gesture(event)
        else:
            return super().event(event)

    def mousePressEvent(self, event):
        if not self.tool:
            self.tool = LineTool(self)
        self.tool.on_click(event)


@dataclass
class Layer:
    canvas_size: QtCore.QSize
    image: QtGui.QImage

    def __init__(self, size=QtCore.QSize(128, 128)):
        self.canvas_size = size
        self.image = QImage(self.canvas_size, QImage.Format_ARGB32)
        self.image.size = self.canvas_size
        self.image.fill(QtCore.Qt.transparent)


class LineTool:
    def __init__(self, parent):
        self.parent = parent
        self.start = None
        self.end = None

    def on_click(self, event):
        canvas_transform: QtGui.QTransform = self.parent.canvas_scale_matrix().inverted()[0]

        point_in_image = canvas_transform.map(QtCore.QPointF(self.parent.image_label.mapFromGlobal(event.globalPos())))
        print(point_in_image)

        point_in_image.setX(math.floor(point_in_image.x()))
        point_in_image.setY(math.floor(point_in_image.y()))

        if not self.start:
            self.start = point_in_image
        elif not self.end:
            self.end = point_in_image

        if self.start and self.end:
            self.line_complete()

    def line_complete(self):
        self.parent.line_complete(self)

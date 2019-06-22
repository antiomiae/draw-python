# utf-8
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtGui import QPainter, QImage, QPixmap

from dataclasses import dataclass


class LayerView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.canvas_size = QtCore.QSize(256, 256)
        self.layer = Layer(self.canvas_size)
        self.tool = None

        layout = QtWidgets.QGridLayout()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        layout.addWidget(scroll_area, 0, 0)
        self.setLayout(layout)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFrameRect(QtCore.QRect(0, 0, 0, 0))
        self.image_label.setFixedSize(self.canvas_size)

        scroll_area.setWidget(self.image_label)
        self.draw_layer()

    def mousePressEvent(self, event):
        if not self.tool:
            self.tool = LineTool(self)
        self.tool.on_click(event)

    def line_complete(self, line):
        p = QPainter(self.layer.image)
        p.drawLine(QtCore.QLineF(line.start, line.end))
        p.end()
        self.tool = None
        self.draw_layer()

    def draw_layer(self):
        self.image_label.setPixmap(QPixmap.fromImage(self.layer.image))


@dataclass
class Layer:
    canvas_size: QtCore.QSize
    image: QtGui.QImage

    def __init__(self, size=QtCore.QSize(128, 128)):
        self.canvas_size = size
        self.image = QImage(self.canvas_size, QImage.Format_ARGB32)
        self.image.size = self.canvas_size
        #breakpoint()
        self.draw_image()

    def draw_image(self):
        self.image.fill(QtCore.Qt.transparent)
        p = QPainter(self.image)
        p.drawLine(QtCore.QLine(0, 0, 128, 128))
        p.end()


class LineTool:
    def __init__(self, parent):
        self.parent = parent
        self.start = None
        self.end = None

    def on_click(self, event):
        if not self.start:
            start = event.pos()
            self.start = self.parent.image_label.mapFrom(self.parent, QtCore.QPoint(start.x()-self.parent.image_label.margin(), start.y()-self.parent.image_label.margin()))
            #breakpoint()
        elif not self.end:
            end = event.pos()
            self.end = self.parent.image_label.mapFrom(self.parent, QtCore.QPoint(end.x(), end.y()))

        if self.start and self.end:
            self.line_complete()

    def line_complete(self):
        self.parent.line_complete(self)

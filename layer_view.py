# utf-8
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtGui import QPainter, QImage, QPixmap


class LayerView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.canvas_size = QtCore.QSize(256, 256)
        self.layer = Layer(self.canvas_size)

        layout = QtWidgets.QGridLayout()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        layout.addWidget(scroll_area, 0, 0)

        self.setLayout(layout)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(self.canvas_size)

        self.image_label.setPixmap(QPixmap.fromImage(self.layer.image))

        scroll_area.setWidget(self.image_label)

    def mousePressEvent(self, event):
        if not self.tool:
            self.tool = LineTool(self)
        self.tool.on_click(event)


class Layer:
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
            self.start = event.localPos()
        elif not self.end:
            self.end = event.localPos()

        if self.start and self.end:
            self.line_complete()

    def line_complete(self):
        pass

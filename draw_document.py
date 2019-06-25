from PySide2 import QtCore
from PySide2 import QtGui
from draw_file import DrawFile
from dataclasses import dataclass

@dataclass
class DrawLayer():
    size: QtCore.QSize
    image: QtGui.QImage

    updated = QtCore.Signal((QtCore.QObject,))

    def __init__(self, size=QtCore.QSize(128, 128)):
        self.size = size
        self.image = QtGui.QImage(self.size, QtGui.QImage.Format_ARGB32)
        self.image.size = self.size
        self.image.fill(QtCore.Qt.transparent)


class DrawDocument(QtCore.QObject):
    document_changed = QtCore.Signal((QtCore.QObject,))

    def __init__(self, file_path=None, size=QtCore.QSize(32, 32)):
        super().__init__()

        self.file_path = file_path
        self.size = size
        self.layers = []

        if file_path:
            self.load_file(self.file_path)

    def load_file(self, file_path):
        draw_file = DrawFile.from_path(file_path)
        canvas_size = QtCore.QSize(draw_file.width, draw_file.height)

        for i in range(draw_file.layer_count):
            info = draw_file.get_layer_data(i)
            with draw_file.get_layer_image_stream(i) as stream:
                buffer = QtCore.QByteArray(stream.read())
                layer = DrawLayer(canvas_size)
                layer.image.loadFromData(buffer)
                self.layers.append(layer)

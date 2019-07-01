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
        self.name = ''
        self.size = size
        self.image = QtGui.QImage(self.size, QtGui.QImage.Format_ARGB32)
        self.image.size = self.size
        self.image.fill(QtCore.Qt.transparent)
        self.hidden = False
        self.blend_mode = 'normal'
        self.alpha = 255


class DrawDocument(QtCore.QObject):
    document_changed = QtCore.Signal((QtCore.QObject,))
    layer_order_changed = QtCore.Signal((QtCore.QObject,))

    def __init__(self, file_path=None, size=QtCore.QSize(32, 32)):
        super().__init__()

        self.file_path = file_path
        self.size = size
        self.layers = []
        self.name = None
        self.palette = []

        if file_path:
            self.load_file(self.file_path)

    def load_file(self, file_path):
        draw_file = DrawFile.from_path(file_path)
        self.name = draw_file.name

        canvas_size = QtCore.QSize(draw_file.width, draw_file.height)
        self.size = canvas_size
        self.palette = draw_file.palette

        self.layers.clear()

        for i in range(draw_file.layer_count):
            info = draw_file.get_layer_data(i)
            print(info)
            with draw_file.get_layer_image_stream(i) as stream:
                buffer = QtCore.QByteArray(stream.read())
                layer = DrawLayer(canvas_size)
                layer.image.loadFromData(buffer)
                layer.hidden = info['hidden']
                layer.blend_mode = info['blendMode']
                layer.alpha = info['alpha']
                layer.name = info['name']
                self.layers.append(layer)

    def move_layer(self, layer, index):
        current_index = self.layers.index(layer)
        if current_index != -1 and current_index != index:
            self.layers.pop(current_index)
            self.layers.insert(index, layer)
            self.layer_order_changed.emit(self)


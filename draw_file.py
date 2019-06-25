from zipfile import ZipFile
import json

class DrawFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self._doc_data = None
        self.file = None

        self.load()

    @staticmethod
    def from_path(path):
        return DrawFile(path)

    def load(self):
        self.ensure_file()
        doc_data = self.doc_data
        canvas_data = doc_data['canvas']
        self.width = canvas_data['width']
        self.height = canvas_data['height']
        self._layer_data = canvas_data['layers']
        self.layer_count = len(self._layer_data)

        self.layers = [self._layer_data[str(i)] for i in range(self.layer_count)]

    def ensure_file(self):
        if not self.file:
            self.file = ZipFile(self.file_path)
        return self.file

    def _get_doc_data(self):
        with self.ensure_file().open('docData.json') as doc_data_file:
            return json.load(doc_data_file)

    @property
    def doc_data(self):
        if not self._doc_data:
            self._doc_data = self._get_doc_data()
        return self._doc_data

    def get_layer_data(self, layer_num):
        return self.layers[layer_num]

    def get_layer_image_stream(self, layer_num):
        if layer_num < 0 or layer_num >= self.layer_count:
            raise 'layer out of bounds'

        path_name = 'layer{}.png'.format(layer_num)

        return self.file.open(path_name)

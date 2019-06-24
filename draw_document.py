from PySide2 import QtCore
from dataclasses import dataclass

@dataclass
class DrawDocument(QtCore.QObject):
    file_path: str

    def __init__(self):
        super().__init__()

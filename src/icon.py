from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import Qt

def nearest_icon(path, sizes=[16, 24, 32, 48, 64]):
    """Create Icon with nearest-neighbor filtering on image
    """
    icon = QIcon()
    src = QImage(path)

    for size in sizes:
        scaled = src.scaled(
            size, size, Qt.KeepAspectRatio, Qt.FastTransformation
        )
        icon.addPixmap(QPixmap.fromImage(scaled))
    return icon

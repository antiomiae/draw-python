from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *


class CurrentColorsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.primary_color = None
        self.secondary_color = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush('#ff0000'))
        painter.setPen(QPen('#ff0000'))
        #painter.drawRect(self.contentsRect())

        swatch_size = QSizeF(self.rect().size())*(3/4)

        offset = QRectF(self.rect()).bottomRight() - QPointF(swatch_size.width(), swatch_size.height())
        painter.fillRect(QRectF(offset, swatch_size), self.secondary_color or 'white')
        painter.fillRect(QRectF(QPointF(0, 0), swatch_size), self.primary_color or 'black')

        painter.end()



from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *


class CurrentColorsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.primary_color = None
        self.secondary_color = None

        self.setLayout(QVBoxLayout())
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self.layout().addWidget(CurrentColorsView(self))
        #self.layout().setSizeConstraint(QLayout.SetMinimumSize)

    def sizeHint(self):
        return QSize(128, 128)

class CurrentColorsView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setContentsMargins(4, 4, 4, 4)
        #self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def sizeHint(self):
        return QSize(128, 128)

    def resizeEvent(self, event):
        w = event.size().width()
        h = event.size().height()

        if w < h:
            self.resize(w, w)
        else:
            self.resize(h, h)

        print('resizeEvent', event.size(), self.size())
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush('#ff0000'))
        painter.setPen(QPen('#ff0000'))

        cr = self.contentsRect()
        swatch_size = QSizeF(cr.size())*(3/4)
        offset = QRectF(cr).bottomRight() - QPointF(swatch_size.width(), swatch_size.height())

        # draw secondary color
        painter.fillRect(QRectF(offset, swatch_size), self.parent().secondary_color or 'white')
        # draw primary color
        painter.fillRect(QRectF(cr.topLeft(), swatch_size), self.parent().primary_color or 'black')

        painter.end()

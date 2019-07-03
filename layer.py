from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


class LayerPanel(QWidget):
    def __init__(self, *args):
        print('init')
        super().__init__(*args)

        self._document = None
        self._toolbar = None
        self.setLayout(QVBoxLayout())

        self._layer_list = LayerList()
        self.layout().addWidget(self._layer_list)

        self.setup_toolbar()

    def register_window(self, main_window):
        print('register_window')
        main_window.document_changed.connect(self.document_changed)

    def document_changed(self, document):
        print('document_changed')

        if document:
            self._document = document
            self._layer_list.set_layers(self._document.layers)
        else:
            self._document = None
            self.clean_up()

    def clean_up(self):
        self._layer_list.set_layers([])

    def layer_order_changed(self, document):
        print('layer_order_changed')
        if document != self._document:
            return

    def setup_toolbar(self):
        self.toolbar = QToolBar(self)
        self.layout().insertWidget(0, self.toolbar)
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.toolbar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        enlarge_icon = QIcon(':/icons/palette_icons_enlarge.png')
        shrink_icon = QIcon(':/icons/palette_icons_shrink.png')
        delete_icon = QIcon(':/icons/palette_icons_delete.png')
        add_icon = QIcon(':/icons/palette_icons_add.png')

        add_action = self.toolbar.addAction(add_icon, 'add', self.handle_add)
        shrink_action = self.toolbar.addAction(shrink_icon, 'shrink palette', self.handle_shrink)
        enlarge_action = self.toolbar.addAction(enlarge_icon, 'enlarge palette', self.handle_enlarge)
        delete_action = self.toolbar.addAction(delete_icon, 'delete', self.handle_delete)

    def handle_add(self):
        pass

    def handle_delete(self):
        pass

    def handle_enlarge(self):
        size = self._layer_list._item_size + QSize(2, 2)
        self._layer_list.set_item_size(size.boundedTo(QSize(128, 128)))

    def handle_shrink(self):
        size = self._layer_list._item_size - QSize(2, 2)
        self._layer_list.set_item_size(size.expandedTo(QSize(32, 32)))


class LayerList(QScrollArea):
    def __init__(self, *args):
        super().__init__(*args)

        self._current_item = None
        self._layers = []
        self._item_size = QSize(75, 50)

        self._item_container = QWidget()
        self.setWidget(self._item_container)

        self._items_layout = QVBoxLayout()
        self._item_container.setLayout(self._items_layout)
        self._items_layout.setSpacing(1)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.setFrameStyle(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundRole(QPalette.Dark)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_item_size(self, size):
        self._item_size = size
        for item in self._items_layout.children():
            item.widget().set_item_size(size)
        # self.update()
        # self.updateGeometry()

    def set_layers(self, layers):
        self._layers = layers
        self.update_list()

    def update_list(self):
        pool = [self._items_layout.takeAt(i).widget() for i in reversed(range(self._items_layout.count()))]

        for layer_index, layer in enumerate(self._layers):
            item = pool and pool.pop() or LayerListItem()
            self._items_layout.addWidget(item)
            item.set_layer(layer)
            item.set_item_size(self._item_size)
            item.focused.connect(self.item_received_focus)

        for item in pool:
            item.deleteLater()

        # self._items_layout.update()
        # self.update()

    def item_received_focus(self, item):
        index = self._layers.index(item._layer)
        if index != -1:
            self.current_layer = item._layer
            if self._current_item:
                self._current_item.set_current(False)
            item.set_current(True)
            self._current_item = item


class LayerListItem(QFrame):
    focused = Signal((QObject,))

    def __init__(self, *args):
        super().__init__(*args)

        self._layer = None
        self._item_size = None
        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundRole(QPalette.Window)

        self.setFocusPolicy(Qt.ClickFocus)

        self.setLayout(QHBoxLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

        self._layer_view_label = QLabel()
        self.layout().addWidget(self._layer_view_label)
        self._layer_view_label.setAutoFillBackground(True)
        # self._layer_view_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        bg = QPixmap(':/textures/bg.png')
        p = self._layer_view_label.palette()
        p.setBrush(QPalette.Window, bg)
        self._layer_view_label.setPalette(p)

        p = self.palette()
        p.setColor(QPalette.Window, QColor('#EEE'))
        self.setPalette(p)
        self.setAutoFillBackground(True)

        self._layer_name_label = QLabel()
        self.layout().addWidget(self._layer_name_label, Qt.AlignCenter)

    def set_layer(self, layer):
        self._layer = layer
        self._layer_view_label.setPixmap(QPixmap(self._layer.image))
        self._layer_name_label.setText(self._layer.name)

    def focusInEvent(self, event: QFocusEvent):
        self.focused.emit(self)

    def set_item_size(self, size):
        new_size = self._layer.image.size.scaled(size, Qt.KeepAspectRatio)
        #self._layer_view_label.setFixedSize(new_size)
        self._layer_view_label.resize(new_size)
        self._layer_view_label.updateGeometry()
        self._layer_view_label.adjustSize()
        self._layer_view_label.update()

    def set_current(self, current):
        if current:
            self.setBackgroundRole(QPalette.Light)
        else:
            self.setBackgroundRole(QPalette.Window)

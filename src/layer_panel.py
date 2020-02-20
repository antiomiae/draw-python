from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *


class LayerPanel(QWidget):
    __style_sheet = """
    QToolButton {
      qproperty-autoRaise: false;
      background: #bbb;
    }
    """
    def __init__(self, *args):
        print('init')
        super().__init__(*args)

        self._document = None
        self._toolbar = None
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet(self.__style_sheet)

        self._layer_list = LayerList()
        self.layout().addWidget(self._layer_list)

        self.setup_toolbar()
        self.restore_settings()

        QApplication.instance().aboutToQuit.connect(self.save_settings)

    def restore_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value('editor/layer_panel/geometry', self.saveGeometry()))

    def save_settings(self):
        settings = QSettings()
        settings.setValue('editor/layer_panel/geometry', self.saveGeometry())
        settings.sync()

    def register_window(self, main_window):
        print('register_window')
        main_window.document_changed.connect(self.document_changed)
        main_window.destroyed.connect(self.save_settings)

    def document_changed(self, document):
        print('LayerPanel document_changed')

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
        print(type(self).__name__, 'handle_enlarge')
        size = self._layer_list.item_size + QSize(2, 2)
        self._layer_list.set_item_size(size.boundedTo(QSize(256, 256)))

    def handle_shrink(self):
        size = self._layer_list.item_size - QSize(2, 2)
        self._layer_list.set_item_size(size.expandedTo(QSize(16, 16)))


class LayerList(QScrollArea):
    def __init__(self, *args):
        super().__init__(*args)

        self._current_item = None
        self._layers = []
        self.current_layer = None
        self.item_size = QSize(75, 50)
        self.setContentsMargins(0, 0, 0, 0)

        self._item_container = QWidget()
        self.setWidget(self._item_container)

        self._items_layout = QVBoxLayout()
        self._item_container.setLayout(self._items_layout)
        self._item_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._items_layout.setSpacing(1)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.setFrameStyle(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundRole(QPalette.Dark)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_item_size(self, size):
        print(type(self).__name__, 'set_item_size')
        self.item_size = size
        for item in (self._items_layout.itemAt(i) for i in range(self._items_layout.count())):
            item.widget().set_item_size(size)

    def set_layers(self, layers):
        self._layers = layers
        self.update_list()

    def update_list(self):
        pool = [self._items_layout.takeAt(0).widget() for _ in range(self._items_layout.count())]

        for item in pool:
            item.setParent(None)
            item.deleteLater()

        for layer_index, layer in enumerate(self._layers):
            item = LayerListItem()
            self._items_layout.addWidget(item)
            item.set_layer(layer)
            item.set_item_size(self.item_size)
            item.focused.connect(self.item_received_focus)

        self._current_item = None

        self.updateGeometry()

    def item_received_focus(self, item):
        index = self._layers.index(item.layer)
        if index != -1:
            self.current_layer = item.layer
            if self._current_item:
                self._current_item.set_current(False)
            item.set_current(True)
            self._current_item = item


class LayerListItem(QFrame):
    focused = Signal((QObject,))

    __stylesheet = """
     LayerListItem {
      /*background: #eee;*/
      margin-top: 1px;
      margin-bottom: 1px;
      margin-left: 2px;
      margin-right: 2px;
     }
    
    LayerListItem[current=true] {
      border: 2px solid #1111ee;
      border-top-width: 1px;
      border-bottom-width: 1px;
      margin: 0px;
    }
    """

    def __init__(self, *args):
        super().__init__(*args)

        self.layer = None
        self._item_size = None
        self.current = False
        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundRole(QPalette.Window)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setStyleSheet(self.__stylesheet)
        self.setProperty('current', False)
        self.setFocusPolicy(Qt.ClickFocus)

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._layer_view_label = LayerImageView()
        self.layout().addWidget(self._layer_view_label)
        self._layer_view_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        bg = QPixmap(':/textures/bg.png')
        p = self._layer_view_label.palette()
        p.setBrush(QPalette.Window, bg)
        self._layer_view_label.setPalette(p)

        self._visibility_button = QToolButton()
        self._visibility_button.setIcon(QIcon(':/icons/layer_icons_eye_open'))
        self._visibility_button.clicked.connect(self.toggle_visible)
        self._visibility_button.setIconSize(QSize(16, 16))
        self.layout().addWidget(self._visibility_button)

        self._name_text = TextEdit()
        self._name_text.editingFinished.connect(self.on_edit_layer_name)
        self.layout().addWidget(self._name_text, Qt.AlignCenter)

    def set_layer(self, layer):
        self.layer = layer
        self._layer_view_label.set_image(self.layer.image)
        self._name_text.setText(self.layer.name)
        self.update_visibility_button()
        self.updateGeometry()

    def focusInEvent(self, event: QFocusEvent):
        self.focused.emit(self)

    def set_item_size(self, size):
        print(type(self).__name__, 'set_item_size')
        self._layer_view_label.max_size = size
        self._layer_view_label.update_size()
        self.updateGeometry()

    def set_current(self, current):
        self.current = current
        self.setProperty('current', current)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def toggle_visible(self):
        self.layer.hidden = not self.layer.hidden
        self.layer.propagate_changes()
        self.update_visibility_button()

    def update_visibility_button(self):
        if not self.layer.hidden:
            self._visibility_button.setIcon(QIcon(':/icons/layer_icons_eye_open'))
        else:
            self._visibility_button.setIcon(QIcon(':/icons/layer_icons_eye_closed'))

    def on_edit_layer_name(self):
        new_name = self._name_text.text()

        if new_name != '':
            self.layer.name = new_name
            self.layer.propagate_changes()


class LayerImageView(QWidget):
    def __init__(self, *args):
        super().__init__(*args)

        self.setAutoFillBackground(True)
        self._image = QImage()
        self.max_size = QSize(128, 128)

    def set_image(self, image):
        self._image = image
        self.update_size()

    def update_size(self):
        if self._image:
            new_size = self._image.rect().size().scaled(self.max_size, Qt.KeepAspectRatio)
            self.setFixedSize(new_size)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.drawImage(self.contentsRect(), self._image)
        painter.end()


class TextEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setFrame(0)
        self.setReadOnly(True)
        self.setStyleSheet('''
        QLineEdit::read-only { background: transparent; }
        ''')

        self.editingFinished.connect(self.on_editing_finished)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        if self.isReadOnly():
            self.setReadOnly(False)
            self.grabKeyboard()
            self.selectAll()

    def on_editing_finished(self):
        self.setReadOnly(True)
        self.deselect()

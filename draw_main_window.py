import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from draw_document import DrawDocument
from draw_window import DrawWindow

class DrawMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._open_draw_documents = []
        self.open_draw_windows = []

        self.mdi_area = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdi_area)

        self._actions = {}
        self.setup_actions()
        self.setup_menus()

        QtWidgets.QApplication.instance().aboutToQuit.connect(self.on_about_to_quit)

        self.reload_windows()

    def reload_windows(self):
        settings = QtCore.QSettings()
        file_paths = settings.value('editor/open_windows', [])

        for path in file_paths:
            document = DrawDocument(path)
            window = DrawWindow(document)
            self.mdi_area.addSubWindow(window)
            window.show()

    def on_about_to_quit(self):
        settings = QtCore.QSettings()
        open_windows = [window.document.file_path for window in self.mdi_area.subWindowList() if window.document.file_path]
        settings.setValue('editor/open_windows', open_windows)

    def setup_actions(self):
        open_file = QtWidgets.QAction('Open')
        open_file.setShortcut(QtGui.QKeySequence.Open)

        new_file = QtWidgets.QAction('New')
        new_file.setShortcut(QtGui.QKeySequence.New)

        save_file = QtWidgets.QAction('Save')
        save_file.setShortcut(QtGui.QKeySequence.Save)

        self._actions['open_file'] = open_file
        self._actions['new_file'] = new_file
        self._actions['save_file'] = save_file

        show_all_windows = QtWidgets.QAction('Show All Windows')
        self._actions['show_all_windows'] = show_all_windows

        hide_all_windows = QtWidgets.QAction('Hide All Windows')
        self._actions['hide_all_windows'] = hide_all_windows

        view_zoom_in = QtWidgets.QAction('Zoom In')
        view_zoom_in.setShortcut(QtGui.QKeySequence.ZoomIn)
        self._actions['view_zoom_in'] = view_zoom_in

        view_zoom_out = QtWidgets.QAction('Zoom Out')
        view_zoom_out.setShortcut(QtGui.QKeySequence.ZoomOut)
        self._actions['view_zoom_out'] = view_zoom_out

        view_toggle_grid = QtWidgets.QAction('Toggle Grid')
        view_toggle_grid.setShortcut(QtGui.QKeySequence.fromString('Ctrl+G'))
        self._actions['view_toggle_grid'] = view_toggle_grid

        for (name, action) in self._actions.items():
            method_name = 'handle_{}'.format(name)
            if hasattr(self, method_name):
                action.triggered.connect(getattr(self, method_name))

    def setup_menus(self):
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self._actions['open_file'])
        file_menu.addAction(self._actions['new_file'])
        file_menu.addAction(self._actions['save_file'])

        view_menu = self.menuBar().addMenu('View')
        view_menu.addAction(self._actions['view_zoom_in'])
        view_menu.addAction(self._actions['view_zoom_out'])
        view_menu.addAction(self._actions['view_toggle_grid'])

        window_menu = self.menuBar().addMenu('Window')
        window_menu.addAction(self._actions['show_all_windows'])
        window_menu.addAction(self._actions['hide_all_windows'])

    def handle_open_file(self, checked):
        settings = QtCore.QSettings()
        open_dir = settings.value('editor/open_file_location') or os.path.expanduser('~')

        file_name, filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', open_dir, 'Pyxel files (*.pyxel)')

        if file_name:
            settings.setValue('editor/open_file_location', os.path.dirname(file_name))

            document = DrawDocument(file_name)
            window = DrawWindow(document)
            self.mdi_area.addSubWindow(window)
            self.open_draw_windows.append(window)
            window.show()

    def handle_show_all_windows(self, checked):
        for window in self.mdi_area.subWindowList():
            window.show()

    def handle_hide_all_windows(self, checked):
        for window in self.mdi_area.subWindowList():
            window.showShaded()

    def handle_view_zoom_in(self, checked):
        w = self.mdi_area.currentSubWindow()
        if w:
            w.zoom_in()

    def handle_view_zoom_out(self, checked):
        w = self.mdi_area.currentSubWindow()
        if w:
            w.zoom_out()

    def handle_view_toggle_grid(self, checked):
        w = self.mdi_area.currentSubWindow()
        if w:
            w.toggle_grid()

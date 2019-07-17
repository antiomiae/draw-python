import sys
import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import resources

from draw_document import DrawDocument
from draw_window import DrawWindow

from palette_panel import PalettePanel
from info_panel import InfoPanel
from layer_panel import LayerPanel
from drawing_tools_widget import DrawingToolsWidget
from current_colors import CurrentColorsWidget


class Logger:
    def __init__(self, parent):
        self.parent = parent
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        self.parent.write_log(message)

    def flush(self):
        self.terminal.flush()


class DrawMainWindow(QtWidgets.QMainWindow):
    document_changed = QtCore.Signal(DrawDocument)

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QtGui.QIcon(':/icons/emblem.png'))

        self._info_bar = None

        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.setFrameStyle(0)
        self.mdi_area.setBackground(QtGui.QBrush(QtGui.QColor('#444')))
        self.setCentralWidget(self.mdi_area)

        p = self.palette()
        p.setColor(QtGui.QPalette.Dark, QtGui.QColor('#444'))
        p.setColor(QtGui.QPalette.Window, QtGui.QColor('#CCC'))
        self.setPalette(p)

        self._actions = {}
        self.setup_actions()
        self.setup_menus()
        self.setup_docks()
        self.setup_toolbars()
        self.setStatusBar(QtWidgets.QStatusBar())

        self.mdi_area.subWindowActivated.connect(self.handle_window_activated)

        QtWidgets.QApplication.instance().aboutToQuit.connect(self.on_about_to_quit)

        self.reload_windows()

    def reload_windows(self):
        settings = QtCore.QSettings()

        self.restoreGeometry(settings.value('editor/geometry'))

        file_paths = settings.value('editor/open_windows', [])

        for path in file_paths:
            document = DrawDocument(path)
            window = DrawWindow(document)
            self.mdi_area.addSubWindow(window)
            window.show()

    def on_about_to_quit(self):
        settings = QtCore.QSettings()
        open_windows = [
            window.document.file_path
            for window in self.mdi_area.subWindowList()
            if window.document.file_path
        ]
        settings.setValue('editor/open_windows', open_windows)
        settings.setValue('editor/geometry', self.saveGeometry())
        settings.sync()

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

        reset_zoom = QtWidgets.QAction('Reset Zoom', self)
        reset_zoom.setShortcut(QtGui.QKeySequence.fromString('Ctrl+0'))
        self._actions['reset_zoom'] = reset_zoom

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
        view_menu.addAction(self._actions['reset_zoom'])
        view_menu.addAction(self._actions['view_toggle_grid'])

        window_menu = self.menuBar().addMenu('Window')
        window_menu.addAction(self._actions['show_all_windows'])
        window_menu.addAction(self._actions['hide_all_windows'])

    def create_dock_widget(self, name, dock_area=QtCore.Qt.RightDockWidgetArea):
        dock = QtWidgets.QDockWidget()
        self.addDockWidget(dock_area, dock)

        #dock.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        dock.setAllowedAreas(dock_area)

        return dock

    def setup_docks(self):
        dock = self.create_dock_widget('palette')
        palette_window = PalettePanel()
        dock.setWidget(palette_window)
        self.document_changed.connect(palette_window.document_changed)

        self.layer_dock = self.create_dock_widget('layers')
        layer_panel = LayerPanel()
        self.layer_dock.setWidget(layer_panel)
        layer_panel.register_window(self)

        dock_2 = self.create_dock_widget('info')
        self.info_panel = InfoPanel()
        dock_2.setWidget(self.info_panel)

        self.current_color_widget = CurrentColorsWidget()
        self.current_color_widget.setMinimumSize(QtCore.QSize(16, 16))

        current_color_dock = self.create_dock_widget('current colors', QtCore.Qt.LeftDockWidgetArea)
        current_color_dock.setWidget(self.current_color_widget)

        self.drawing_tools_widget = DrawingToolsWidget()
        tool_dock = self.create_dock_widget('drawing tools', QtCore.Qt.LeftDockWidgetArea)
        tool_dock.setWidget(self.drawing_tools_widget)

    def setup_toolbars(self):
        self.top_toolbar = self.addToolBar('toolbar')

    def handle_open_file(self, checked):
        settings = QtCore.QSettings()
        open_dir = settings.value('editor/open_file_location') or os.path.expanduser('~')

        file_name, filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', open_dir, 'Pyxel files (*.pyxel)')

        if file_name:
            settings.setValue('editor/open_file_location', os.path.dirname(file_name))

            document = DrawDocument(file_name)
            window = DrawWindow(document)
            self.mdi_area.addSubWindow(window)
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

    def handle_window_activated(self, window):
        if window:
            print('DrawMainWindow emitting document_changed')
            self.document_changed.emit(window.document)

    def handle_reset_zoom(self):
        w = self.mdi_area.currentSubWindow()
        if w:
            w.reset_zoom()

    def write_log(self, message):
        if self.info_panel:
            self.info_panel.write_text(message)

    def resizeEvent(self, event):
        print('DrawMainWindow resizeEvent', event)
        return super().resizeEvent(event)

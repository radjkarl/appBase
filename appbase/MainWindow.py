# -*- coding: utf-8 -*-
# this pkg:
from __future__ import print_function

from qtpy import QtGui, QtWidgets

from appbase.mainWindowRessources.menubar import MenuBar
from appbase.Application import Application


class MainWindow(QtWidgets.QMainWindow):
    """
    template for QMainWindow including:

    * a menu bar with all common features
    * fullscreen with F11
    * changed window title when saved under a new name
    * Preferences in Menubar->File
    * autosave
    * close dialog
    """

    def __init__(self, title=''):
        super(MainWindow, self).__init__()
        self.app = QtWidgets.QApplication.instance()
        if not isinstance(self.app, Application):
            print('Error: QApp is no instance from appbase.Application')
            return

        def fn(state):
            return self.setTitlePath(self.app.session.path)

        self.app.session.sigRestore.connect(fn)
        self.app.session.sigSave.connect(fn)

        self._window_title = title
        self._window_title_additive = ''
        self._window_title_path = ''
        m = MenuBar()
        self.setMenuBar(m)
        self._setTitle()
        # Shortcuts
        sc = m.shortcutsWidget
        sc.addShortcut('Alt+F4', 'Close current window')
        sc.addShortcut('F11', 'Fullscreen')
        k = QtGui.QKeySequence
        sc.addShortcut(k(k.Undo).toString(), 'Undo last action')
        sc.addShortcut(k(k.Redo).toString(), 'Redo last action')
        sc.addShortcut(k(k.Save).toString(), 'Save current session')
        s = k(k.SaveAs).toString()
        if s:
            # not every OS has this shortcut:
            sc.addShortcut(s, 'Save current session under a new name')

    def setTitleAdditive(self, value=''):
        if value:
            self._window_title_additive = '- %s' % value
        else:
            self._window_title_additive = value
        self._setTitle()

    def setTitlePath(self, value=''):
        if value:
            self._window_title_path = '- %s' % value
        else:
            self._window_title_path = ''
        self._setTitle()

    def _setTitle(self):
        self.setWindowTitle('%s %s %s' % (self._window_title,
                                          self._window_title_additive,
                                          self._window_title_path))

    def closeEvent(self, evt):
        if self.app.session.opts['showCloseDialog']:
            b = _CloseDialog(self)
            ret = b.exec_()
            if ret == QtWidgets.QMessageBox.Save:
                self.app.session.save()
            elif ret == QtWidgets.QMessageBox.Cancel:
                return evt.ignore()
        return evt.accept()


class _CloseDialog(QtWidgets.QMessageBox):

    def __init__(self, mainWindow):
        QtWidgets.QMessageBox.__init__(self, mainWindow)
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setText("Close the program...")
        self.setInformativeText("Save changes?")
        self.setStandardButtons(
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)

        c = QtWidgets.QCheckBox("don't ask me again")
        c.clicked.connect(
            lambda val: mainWindow.app.session.opts.__setitem__(
                'showCloseDialog', not val))
        self.layout().addWidget(c, 4, 0, 7, 0)


if __name__ == '__main__':
    import sys

    def save(session):
        print('saveTest')
        print(session.path)

    def restore(session):
        print('restore')

    app = Application([])
    win = MainWindow(title='Hello World')
    # CONNECT OWN SAVE/RESTORE FUNCTIONS TO THE SESSION
    app.session.sigSave.connect(save)
    app.session.sigRestore.connect(restore)

    win.show()
    sys.exit(app.exec_())

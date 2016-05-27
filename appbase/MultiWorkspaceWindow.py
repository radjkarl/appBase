from MainWindow import MainWindow

from PyQt4 import QtGui, QtCore



class MultiWorkspaceWindow(MainWindow):
    '''Adding workspace management to appbase.MainWindow

    * 'Workspace' menu in menu bar
    * Switch between workspaces with [Ctrl]+[Page up/down]
    * Add workspace with [Ctrl]+[W]
    * Remove current workspace with [Ctrl]+[Q]
    '''

    def __init__(self, workspaceClass, *args, **kwargs):
        '''
        workspaceClass needs to have the following methods:

        * def setActive -> called when workspace is activated
        * def setInactive -> called when workspace is deactivated
        '''
        MainWindow.__init__(self, *args, **kwargs)

        self._workspace_cls = workspaceClass

        self.setCentralWidget(QtGui.QStackedWidget())

        # APPEND MENUBAR
        m = self.menuBar()
        w = m.menu_workspace = QtGui.QMenu('&Workspace')
        m.insertMenuBefore(m.menu_help, w)

        action_add = QtGui.QAction('&Add', w)
        action_add.triggered.connect(self.addWorkspace)
        action_add.setShortcuts(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_W))
        w.addAction(action_add)

        action_close = QtGui.QAction('&Close current', w)
        action_close.triggered.connect(self.closeCurrentWorkspace)
        action_close.setShortcuts(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Q))
        w.addAction(action_close)

        action_next = QtGui.QAction('&Next', w)
        action_next.triggered.connect(self.showNextWorkspace)
        action_next.setShortcuts(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_PageUp))
        w.addAction(action_next)

        action_previous = QtGui.QAction('&Previous', w)
        action_previous.triggered.connect(self.showPreviousWorkspace)
        action_previous.setShortcuts(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_PageDown))
        w.addAction(action_previous)

        self._menu_workspaces = QtGui.QMenu('Set', w)
        self._menu_workspaces.aboutToShow.connect(self._listWorkspacesInMenu)
        w.addMenu(self._menu_workspaces)

        # Shortcuts
        sc = self.menuBar().shortcutsWidget
        sc.addShortcut('Alt+w', 'Add Workspace')
        sc.addShortcut('Alt+q', 'Close current Workspace')
        sc.addShortcut('Alt+PageUp', 'Show next Workspace')
        sc.addShortcut('Alt+PageDown', 'Show previous Workspace')


    def workspaces(self, index=None):
        '''return generator for all all workspace instances'''
        c = self.centralWidget()
        if index is None:
            return (c.widget(n) for n in range(c.count()))
        else:
            return c.widget(index)


    def currentWorkspace(self):
        return self.centralWidget().currentWidget()


    def addWorkspace(self):
        w = self.currentWorkspace()
        if w:
            w.setInactive()
        w = self._workspace_cls(self)
        c = self.centralWidget()
        i = c.addWidget(w)
        c.setCurrentIndex(i)
        self.setTitleAdditive('[%s/%s]' % (i+1, c.count() ) )
        return w


    def closeWorkspace(self, ws):
        ws.close()
        self.centralWidget().removeWidget(ws)
        ws.deleteLater()


    def closeCurrentWorkspace(self):
        c = self.centralWidget()
        self.closeWorkspace(c.currentWidget())
        if c.count() == 0:
            self.addWorkspace()
        else:
            c.setCurrentIndex(c.count()-1)
            self.setTitleAdditive('[%s/%s]' % (c.count(), c.count() ) )


    def showNextWorkspace(self):
        c = self.centralWidget()
        i = c.currentIndex()
        if i >= c.count()-1:
            return  # at the end
        self.showWorkspace(i+1)


    def showWorkspace(self, i):
        c = self.centralWidget()
        c.currentWidget().setInactive()
        c.setCurrentIndex(i)
        w = c.currentWidget()
        w.setActive()
        self.setTitleAdditive('[%s/%s]' %(i+1, c.count() ) )


    def showPreviousWorkspace(self):
        c = self.centralWidget()
        i = c.currentIndex()
        if i == 0:
            return
        self.showWorkspace(i-1)


    def _listWorkspacesInMenu(self):
        c = self.centralWidget()
        self._menu_workspaces.clear()
        for i in range(c.count()):
            if i == c.currentIndex():
                t = '[%s] <-' % str(i+1)
            else:
                t = '[%s]' % str(i+1)
            a = QtGui.QAction(t, self._menu_workspaces)

            a.triggered.connect(lambda clicked, i=i, self=self: self.showWorkspace(i))
            self._menu_workspaces.addAction(a)



if __name__ == '__main__':
    from appbase.Application import Application
    import sys

    class Workspace(QtGui.QTextEdit):
        def setInactive(self):
            self.append('inactivated')

        def setActive(self):
            self.append('activated')

    app = Application([])
    win = MultiWorkspaceWindow(Workspace, title='Hello World')

    win.addWorkspace()
    win.addWorkspace()

    win.currentWorkspace().setText("""This is workspace [2]
You can switch between different workspaces via Menubar->Workspace->Next/Previous
-------""")

    win.show()
    sys.exit(app.exec_())


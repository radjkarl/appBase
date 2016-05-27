from PyQt4 import QtGui



class Server(QtGui.QSystemTrayIcon):
    '''
    a system tray icon to 
    
    * show/hide the current session [left mouse button]
    * show options(load, save, new) [right mouse button]
    '''

    def __init__(self, win, parent=None):
        name = win.windowTitle()
        icon = win.windowIcon()
        QtGui.QSystemTrayIcon.__init__(self, QtGui.QIcon(icon), parent)
        self.app = QtGui.QApplication.instance()


        menu = QtGui.QMenu(parent)
        if win:
            self.a_show = menu.addAction("show")
            self.a_hide = menu.addAction("hide")
            self.a_show.triggered.connect(lambda: [win.show(), self.a_hide.setVisible(True), self.a_show.setVisible(False)]) 
            self.a_hide.triggered.connect(lambda: [win.hide(), self.a_hide.setVisible(False), self.a_show.setVisible(True)]) 
            if win.isVisible():
                self.a_show.setVisible(False) 
            else:
                self.a_hide.setVisible(False)
            menu.addSeparator()
                
        menu.addAction("New").triggered.connect(self.app.session.new)
        menu.addAction("Open").triggered.connect(self.app.session.open)
        menu.addAction("Exit").triggered.connect(self.app.quit)
        self.setContextMenu(menu)

        self.activated.connect(self.clickTrap)
        self.show()
        self.showMessage(name, '...started', QtGui.QSystemTrayIcon.Information)


    def toggleShowHide(self):
        if self.a_show.isVisible():
            self.a_show.trigger()
        else:
            self.a_hide.trigger()


    def showMainWindow(self):
        self.app.activeWindow().show()


    def clickTrap(self, value):
        if value == self.Trigger: #left click!
            self.toggleShowHide()



if __name__ == '__main__':
    import sys
    from Application import Application
    from MainWindow import MainWindow
    
    app = Application([])
    win = MainWindow('dummy')

    s=Server(win)
    s.show()
    sys.exit(app.exec_())
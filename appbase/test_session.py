# -*- coding: utf-8 -*-


import sys
from appbase.application import Application
from appbase.widgets.mainwindow.window import MainWindow
from appbase.widgets.textEditor import TextEditor
from appbase.widgets.dockArea import DockArea
from appbase.widgets.dock import Dock
from appbase. widgets.table import Table
#from QtRec import QtGui


app = Application([])
win = MainWindow(title='Hello World')


area = DockArea()
win.setCentralWidget(area)
d1 = Dock('one')#TODO: fold/unfold
d1.addWidget(Table())
area.addDock(d1)

win.show()


win2 = TextEditor()
win2.show()

sys.exit(app.exec_())

# -*- coding: utf-8 -*-
#from QtRec.QtGui import QApplication

#import sys
from appBase import identity
from appBase.application import Application
from appBase.widgets.window import Window
from appBase.widgets.dockArea import DockArea
from appBase.widgets.dock import Dock
from appBase.widgets.table import Table


def main():
	#app = QApplication(sys.argv)
	app = Application(identity)
	win = Window(app)#title='Hello World')
	area = DockArea()
	win.setCentralWidget(area)
	d1 = Dock('one')#TODO: fold/unfold
	d1.addWidget(Table())
	d2 = Dock('one')

	area.addDock(d1)
	area.addDock(d2)


	#win.show()
	app.start(main, locals())
	


if __name__ == '__main__':
	main()
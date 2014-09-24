# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

#own
#import nIOp

#foreign
#import os

from QtRec import QtGui

from mainWindowRessources.menubar import MenuBar
#import appbase
try:
	from . import Application
except:
	from appbase import Application

#from fancywidgets.messageDock import MessageDock
#from fancywidgets.dockArea import DockArea



class MainWindow(QtGui.QMainWindow):
	'''
	default class to build Qt-windows for nIOp
	including the nIOp-icon and fullscreen with F11
	'''
	def __init__(self, title=''):
		super(MainWindow, self).__init__()
		self.app = QtGui.QApplication.instance()

		if not isinstance(self.app, Application):
			print 'Error: QApp is no instance from appbase.Application'
			return
		self.app.session.sigPathChanged.connect(self.setTitlePath)

		self._window_title = title
		self._window_title_additive = ''
		self._window_title_path = ''
		
		self.setMenuBar(MenuBar())
		self._setTitle()


	def setTitleAdditive(self, value=''):
		if value:
			self._window_title_additive = '- %s' %value
		else:
			self._window_title_additive = value		
		self._setTitle()


	def setTitlePath(self, value=''):
		if value:
			self._window_title_path = '- %s' %value
		else:
			self._window_title_path = value
# 		#if self.app:
# 		if self._window_title:
# 			if path:
# 				title = "%s || %s" %(self._window_title,path)
# 			else:
# 				title = self._window_title
# 		else:
# 			title = path
		self._setTitle()
		
		
	def _setTitle(self):
		##if path.endswith('.pyz'):
		#title += ' || %s'%path
		self.setWindowTitle('%s %s %s' %(self._window_title, 
										self._window_title_additive, 
										self._window_title_path) )






if __name__ == '__main__':
	#TODO: TEST into docstring
	from appbase import Application
	import sys
	app = Application([])
	#from widgets.window import Window
	#app = Application('Hello World')
	win = MainWindow(title='Hello World')
	win.show()
	#app.start()
	sys.exit(app.exec_())
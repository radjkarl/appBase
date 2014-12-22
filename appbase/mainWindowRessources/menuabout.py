# -*- coding: utf-8 -*-
from PyQt4 import QtGui

class MenuAbout(QtGui.QWidget):
#TODO: create
	def __init__(self, parent=None):
		self.app = QtGui.QApplication.instance()

		super(MenuAbout, self).__init__(parent)
		self.setWindowTitle('About')


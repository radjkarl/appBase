# -*- coding: utf-8 -*-
from QtRec import QtGui, QtCore
#import os
#from fancywidgets.pyQtBased.FwMinimalTextEditor import FwMinimalTextEditor


#from fancytools.os.userName import userName
#import appbase



class MenuAbout(QtGui.QWidget):
#TODO: erstellen
	def __init__(self, parent=None):
		self.app = QtGui.QApplication.instance()

		super(MenuAbout, self).__init__(parent, logparent=self.app)
		self.setWindowTitle('About')


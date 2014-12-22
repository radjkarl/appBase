# -*- coding: utf-8 -*-

#this pkg:
from _Session import Session
#foreign:
from PyQt4 import QtGui
import sys


class Application(QtGui.QApplication):
	__doc__ = Session.__doc__


	def __init__(self, *args):
		QtGui.QApplication.__init__(self, *args)
		#add session features (load, save, restore state etc) can be found in:
		self.session = Session(sys.argv)
		#tell the session when to run the quit procedure:
		self.lastWindowClosed.connect(self.session.quit)

		if sys.platform.startswith("win"):
			# Don't display the Windows GPF dialog if the invoked program dies.
			# See comp.os.ms-windows.programmer.win32
			# How to suppress crash notification dialog?, Jan 14,2004 -
			# Raymond Chen's response [1]
			import ctypes
			SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
			ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);


	def exec_(self):
		self.session.restoreCurrentState()
		return QtGui.QApplication.exec_()



if __name__ == '__main__':
	app = Application([])
	win = QtGui.QMainWindow()
	win.show()
	sys.exit(app.exec_())


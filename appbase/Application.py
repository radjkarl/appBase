# -*- coding: utf-8 -*-



from _Session import Session


from QtRec import core, QtGui

import sys



class Application(QtGui.QApplication):#Structure):
	'''
		* extract the opened (as pyz-zipped) session in a temp folder
		* create 2nd temp-folder for sessions to be saved
		* send a close signal to all child structures when exit
		* write a log file with all output
		* enable icons in menues of gnome-sessions
		* gives option of debug mode
	'''
	def __init__(self, *args):
		QtGui.QApplication.__init__(self, *args)
		self.session = Session(sys.argv)



if __name__ == '__main__':
	core.print_class_not_found = False

	from appbase.MainWindow import MainWindow

	app = Application([])
	win = MainWindow(title='Hello World')
	win.show()
	
	sys.exit(app.exec_())


# -*- coding: utf-8 -*-


#from structure import Structure

import appbase
from appbase.widgets import dialogs
from appbase.launcher import Launcher
#from appbase import utils

#own
from fancytools.os import PathStr, legalizeFilename
from fancytools.utils import Logger

#foreign
import tempfile
import os
import sys
import atexit
import shutil
import distutils
from zipfile import ZipFile


import __main__

import QtRec
from QtRec import QtCore, QtGui




class _Session(QtCore.QObject):
	'''
		* extract the opened (as pyz-zipped) session in a temp folder
		* create 2nd temp-folder for sessions to be saved
		* send a close signal to all child structures when exit
		* write a log file with all output
		* enable icons in menues of gnome-sessions
		* gives option of debug mode
	'''

	sigPathChanged = QtCore.pyqtSignal(object)#path
	sigSave = QtCore.pyqtSignal(object)#save-dir

	def __init__(self):
		QtCore.QObject.__init__(self)
		MAX_N_LOG_FILES = 30
		ENABLE_GUI_ICONS = True
		#make temp-dir
			#the directory where the content of the *pyz-file will be copied:
		self.tmp_dir_session = PathStr(tempfile.mkdtemp('%s_session' %__name__))
			#dir containing all items to save into a new *pyz:
		self.tmp_dir_save_session = PathStr(tempfile.mkdtemp('%s_save_session' %__name__))
			#a work-dir for temp. storage:
		self.tmp_dir_work = PathStr(tempfile.mkdtemp('%s_work' %__name__))


		self._icons_enabled = False

		(pathName, self.debug_mode, createlog, QtRec.restore) = self._inspectArguments()
		#TODO: brauchen wir eigentlich 2 forder _tmp und _tmp_save? kann nicht beides in einem sein?
		if pathName.endswith('.pyz'):
			# this script was opend out from a zip-container (named as '*.pyz')
			self._path = PathStr(pathName)
			self.dir = self._path.dirname().abspath()
			# extract the zip temporally
			ZipFile(self._path,'r').extractall(path=self.tmp_dir_session)
			#move the log files to the 'to-save-dir' that those will be saved again
			for fname in ('log','save', '__main__.py'):
				folder = self.tmp_dir_session.join(fname)
				if folder.exists():
					folder.move(self.tmp_dir_save_session)
		else:
			self.dir = Launcher.rootDir()
			#print self.dir
			self._path = None#self.dir.join('unknown.pyz')
			self.tmp_dir_save_session.mkdir('log')
			self.tmp_dir_save_session.mkdir('save')


		#create new log-filename
		logFolder = self.tmp_dir_save_session.join('log')
		d = logFolder.listdir()
		if d:
			d.sort()
			#...as last log-number +1
			logfilename = logFolder.join( '%s.log' %str(int(d[-1][:-4]) + 1 ))
			#save only the last MAX_N_LOG_FILES
			for f in d[MAX_N_LOG_FILES:]:
				logFolder.remove(f)
		else:
			logfilename = logFolder.join('1.log')

		#create new save-filename
		savefolder = self.tmp_dir_save_session.join('save')
		d = savefolder.listdir()

		QtRec.log_file_name = self.tmp_dir_work.join('save.py')
		if d:
			d.sort()
			#...as last save-number +1
			self._save_file_name = savefolder.join( '%s.py' %str(int(d[-1][:-3]) + 1 ))
			#create one singe file form all saved ones
			with open(QtRec.log_file_name, "wb") as outfile:
				for f in d:
					with open(savefolder.join(f), "rb") as infile:
						outfile.write(infile.read())
		else:
			#save empty
			self._save_file_name = savefolder.join('1.py')


		if createlog:
			#write stout to file:
			self.log_file = file(logfilename, 'a')
			logger = Logger(sys.stdout, self.log_file)
			sys.stdout = logger
			sys.stderr = logger

		#enable icons in all QMenuBars only for this programm if generally disabled
		if ENABLE_GUI_ICONS:
			if os.name == 'posix':#linux
				this_env = str(os.environ.get('DESKTOP_SESSION'))
				relevant_env = 'gnome', 'gnome-shell', 'ubuntustudio', 'xubuntu'
				if this_env in relevant_env:
					if 'false' in os.popen( #if the menu-icons on the gnome-desktop are disabled
					'gconftool-2 --get /desktop/gnome/interface/menus_have_icons').read():
						print 'enable menu-icons'
						os.system(
					'gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons True')
						self._icons_enabled = True

		#execute the following functions before the programm ends:
		atexit.register(self.quit)

		#Timer
		path= self.dir.join('autoSave.pyz')
		self.timerAutosave = QtCore.QTimer()
		self.autosave_interval = 5
		self.timerAutosave.setInterval(self.autosave_interval*60*1000)
		self.timerAutosave.timeout.connect(lambda path=path: self.saveAs(path))


	#TODO: copy evtl. in PathStr rein
	def addFileToSave(self,filePath, rename=''):
		#extract the filename and decode into a zip-friendly format
		if rename:
			fileName = rename
		else:
			fileName = os.path.split(filePath)[1]
			fileName = legalizeFilename(fileName)#.decode('cp437')
		shutil.copyfile( filePath, self.tmp_dir_save_session.join(fileName) )
		return fileName


	def addContentToSave(self, content, fileName):
		with file(self.tmp_dir_save_session.join(fileName),'w') as f:
			f.write(content)


	def getSavedFile(self,filePath):
		t = self.tmp_dir_session.join(filePath)
		if t.exists():
			return t


	def getSavedContent(self,filePath):
		t = self.getSavedFile(filePath)
		if t:
			with open(t,'r') as content:
				return content.read()


	@property
	def path(self):
		'''dirname + sessionname e.g. /home/USER/.../test.pyz'''
		return self._path


	@path.setter
	def path(self, name):
		self._path = name
		self.sigPathChanged.emit(name)


	def quit(self):
		print 'exiting...'
#		self._recursiveClose(self)
		if self._icons_enabled:
			print 'disable menu-icons'
			os.system( #restore the standard-setting for seeing icons in the menus
			'gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons False')

	#	appbase.setRootDir()

		if self.debug_mode:
			raw_input("Press any key to end the session...")

	#	super(_Session,self).quit()


	def _inspectArguments(self):
		'''inspect the command-line-args and give them to appBase'''
		d = os.path.dirname(sys.argv[0])
		if d and appbase.__path__[0].startswith(d): #executed from installpath
			progName = os.path.basename(sys.argv[0])
			folder = Launcher.rootDir()
			#if not folder:
			#	folder = PathStr.home()
			projectName = folder.join(progName)
		else:
			projectName =sys.argv[0]
		args = sys.argv[1:]
		debugMode = False
		createlog = True
		restore = True
		for arg in args:
			if arg in ('-h','--help'):
				self._showHelp()
			elif arg in ('-d','--debug'):
				print 'RUNNGING IN DEBUG-MODE'
				debugMode = True
			elif arg in ('-l','--nolog'):
				print 'CREATE NO LOG'
				createlog = False
			elif arg in ('-n','--new'):
				print 'START A NEW SESSION - DONT LOAD SAVED PROPERTIES'
				restore = False
			else:
				return self._showHelp()
		return projectName, debugMode, createlog, restore


	def _showHelp(self):
		sys.exit('''
	appBase-sessions can started with the following arguments:
		[-h or --help] - show the help-page
		[-d or --debug] - run in debuging-mode
		[-l or --nolog] - create no log file
		[-n or --new] - start a new session, don'l load saved properties
		''')


	def newAdd(self):
		pass #TODO


	def newReplace(self):
		pass #TODO


	def save(self):
		if self._path:
			self._save(self._path)
		else:
			self.saveAs()


	def saveAs(self):
		filename = dialogs.getSaveFileName(filter="*.pyz")
		if filename:
			self.path = filename
			self._save(self.path)


	def openAdd(self):
		filename = dialogs.getOpenFileName(filter="*.pyz")
		if filename:
			#get the absolute path to the python-executable
			p = distutils.spawn.find_executable("python")
			#start an indepentent python-process
			os.spawnl(os.P_NOWAIT, p, 'python', '%s' %filename)


	def openReplace(self):
		filename = dialogs.getOpenFileName(filter="*.pyz")
		if filename:
			#get the absolute path to the python-executable
			p = distutils.spawn.find_executable("python")
			self.exit()#ensure all sources were closed etc.
			os.execv(p, [p, '%s' %filename])


	def _saveDir(self, dirpath):
		'''copy a dir to the zip-file'''
		basedir = dirpath
		for root, dirs, files in os.walk(dirpath):
			dirname = root.replace(basedir, '')
			for f in files:
				self._zipFile.write( os.path.join(root,f), os.path.join(dirname,f) )


	def _save(self, name):
		print 44
		self.sigSave.emit(self.tmp_dir_save_session)
		QtRec.saveAs(self._save_file_name)
		if not self.tmp_dir_save_session.join('__main__.py').exists():
			#because opened from regular .py
			self.addFileToSave(__main__.__file__, '__main__.py')
		with ZipFile(name,'w') as self._zipFile:
			#files written in tmp/appBase:
			self._saveDir(self.tmp_dir_save_session)
		print "===========\neverything saved in a zipped *.pyz: %s" %name




	def _writeToZip(self, name, folder='',content=None, removeSource=False):
		folder = PathStr(folder)
		#create temp.file containing all saved information
		if content:
			with open(name, "w") as prefFile:
				prefFile.write(str(content))
			path = PathStr(name).filename()
		else:
			path = name
		#print name, path, folder,999
		self._zipFile.write(name, folder.join(path))
		#remove tempfile
		if content or removeSource:
			os.remove(name)



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
		self.session = _Session()



if __name__ == '__main__':
	from appbase.widgets.mainwindow.window import MainWindow
	from appbase.widgets.textEditor import TextEditor
	from appbase.widgets.dockArea import DockArea
	from appbase.widgets.dock import Dock
	from appbase. widgets.table import Table
	from QtRec import QtGui


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


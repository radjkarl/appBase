# -*- coding: utf-8 -*-
import appbase

from PyQt4 import QtGui, QtCore

from fancywidgets.pyQtBased.FwMinimalTextEditor import FwMinimalTextEditor
from fancywidgets.pyQtBased.Dialogs import Dialogs
from fancywidgets.pyQtBased.FingerTabWidget import FingerTabWidget

from fancytools.os.userName import userName


_dialogs = Dialogs()


class _TabSession(QtGui.QWidget):
	'''
	The fingerTab 'session' in the preferences widget
	'''
	def __init__(self, prefWindow):
		super(_TabSession, self).__init__()
		self._pref_window = prefWindow
		prefWindow.sigClosed.connect(self._restoreLastScreenshotWindow)

		self.app = QtGui.QApplication.instance()
		
		self.app.session.sigSave.connect(self._save)
		self.app.session.sigRestore.connect(self._restore)
		
		self.opts= {'iconPath':None}
		
		vlayout = QtGui.QVBoxLayout()
		self.setLayout(vlayout)
		
		qtrecPrefs = QtGui.QGroupBox("Record Activity")
		qtrecLayout = QtGui.QVBoxLayout()
		qtrecPrefs.setLayout(qtrecLayout)
		vlayout.addWidget(qtrecPrefs)

		l = QtGui.QHBoxLayout()
		l.addWidget(QtGui.QLabel('max. saved states'))
		self.maxSessions = QtGui.QSpinBox()
		self.maxSessions.setRange(1,1000)
		self.maxSessions.valueChanged.connect(
			lambda val: self.app.session.opts.__setitem__('maxSessions', val))
		l.addWidget(self.maxSessions)
		qtrecLayout.addLayout(l)
		
		self.interval = QtGui.QLabel()
		
		self.slider = QtGui.QSlider(QtCore.Qt.Orientation(1), self)#1...horizontal
		self.slider.sliderMoved.connect(self._updateInterval)
		
		qtrecLayout.addWidget(self.interval)
		qtrecLayout.addWidget(self.slider)

		file_desc = QtGui.QGroupBox('File Information')
		layout = QtGui.QVBoxLayout()

		self.iconChoose = QtGui.QComboBox()
		self._iconPath = None
		
		self.iconChoose.addItem ('Default')

		self.iconChoose.addItem('Individual')
		self.iconChoose.activated[unicode].connect(self._cooseIndividualIcon)
		
		iconLayout = QtGui.QHBoxLayout()
		iconLayout.addWidget(QtGui.QLabel('Icon:'))
		iconLayout.addWidget(self.iconChoose)
		layout.addLayout(iconLayout)
		
		#CHOOSE A SCREENSHOT A SHOW IN THE LAUNCHER DETAILS AREA
		self._lastSchreenshotWindow = None
		self._screenshot_from_window = None
		screenshotLayout = QtGui.QHBoxLayout()
		screenshotLayout.addWidget(QtGui.QLabel('Screenshot:'))
		self._screenshotChoose = QtGui.QComboBox()
		self._screenshotChoose.currentIndexChanged.connect(self._chosenScreenshotWindowChanged)
		screenshotLayout.addWidget(self._screenshotChoose)
		layout.addLayout(screenshotLayout)
		
		#CREATE A DESCRIPTION TEXT
		self.descritionEditior = FwMinimalTextEditor(self)
		
		descriptionText = ''
		if self.app:
			descriptionText = self.app.session.getSavedContent('description')
		if descriptionText:
			self.descritionEditior.text.setText(descriptionText)
		else:
			self.descritionEditior.text.setText(self._defaultDescription())
		layout.addWidget(self.descritionEditior)
		file_desc.setLayout(layout)
		vlayout.addWidget(file_desc)


	def _fillScreenshotChoose(self):
		self._screenshotChoose.clear()
		self._name_2_win = {}
		n = 0
		for win in self._availWindows():
				n += 1
				title = unicode(win.windowTitle())
				if not title:
					title = 'Window ' + str(n)
				self._name_2_win[title] = win
				self._screenshotChoose.addItem(title)
		self._screenshot_from_window = self._name_2_win.values()[0]


	def _availWindows(self):
		'''
		returns a list of all widgets, that are:
		* windows
		* visible
		* not the preferences window
		'''
		return [win for win in self.app.topLevelWidgets()
			if not win.parent() and win.isVisible() and win != self._pref_window]


	def _chosenScreenshotWindowChanged(self, index):
		self._restoreLastScreenshotWindow()
		title = self._screenshotChoose.itemText(index)
		#only indicate the window (e.g. by changing color) if:
		# the window has a title
		# there are more than one window to choose from
		if title and len(self._name_2_win) > 1:
			win = self._name_2_win[unicode(title)]
			p = win.palette()
			self._lastSchreenshotWindow = (win, win.autoFillBackground(), p.color(win.backgroundRole()) )
			win.setAutoFillBackground(True)
			p.setColor(win.backgroundRole(), QtCore.Qt.red)
			win.setPalette(p)
			self._screenshot_from_window = win


	def _restoreLastScreenshotWindow(self):
		if self._lastSchreenshotWindow:
			#restore last
			(win, autoFill, color) = self._lastSchreenshotWindow
			win.setAutoFillBackground(autoFill)
			p = win.palette()
			p.setColor(win.backgroundRole(), color)
			win.setPalette(p)


	def _save(self, session):
		if not self._screenshot_from_window:
			self._screenshot_from_window = self._availWindows()[0]
		pixmap =  QtGui.QPixmap.grabWidget(self._screenshot_from_window)
		pixmap.save(session.tmp_dir_save_session.join('screenshot.png'), 'png')
		if self._iconPath:
			session.addFileToSave(self.opts['iconPath'], 'icon')
		session.addContentToSave(self.descritionEditior.text.toHtml(), 'description.html')


	def update(self):
		if not self.app.session.opts['autosave']:
			self.slider.setSliderPosition(99)
			self._updateInterval(99, False)
		else:
			a = self.app.session.opts['autosaveIntervalMin']
			self.slider.setSliderPosition(a)
			self._updateInterval(a, False)
		self.maxSessions.setValue(self.app.session.opts['maxSessions'])
	
	
	def _restore(self):
		self.descritionEditior.text.setText(
			self.app.session.getSavedContent('description.html') )
		iconPath = self.app.session.getSavedFile('icon')
		self.opts['iconPath'] = iconPath


	def showEvent(self, event):
		self._fillScreenshotChoose()
		super(_TabSession, self).showEvent(event)


	def _defaultDescription(self):
		return '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-style:italic; text-decoration: underline;">- no descrition found -</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">create one in <span style=" font-weight:600;">File-&gt;Preferences</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt;">Example</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Editor:     %s</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Project:</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">State:</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;"><br /></p></body></html>
''' %userName()


	def _cooseIndividualIcon(self, txt):
		if txt == 'Individual':
			i = _dialogs.getOpenFileName(directory=appbase.icon_path)
			if i:
				self.opts['iconPath'] = i


	def _updateInterval(self, time_min, updateOpts=True):
		if time_min == 0:
			time_min = 0.1
		if time_min == 99:
			self.interval.setText("Autosave: never")
			if self.app and updateOpts:
				self.app.session.opts['autosave'] = False
		else:
			self.interval.setText("Autosave: %s min" %time_min)
			if self.app and updateOpts:
				self.app.session.opts['autosaveIntervalMin'] = time_min
				self.app.session.opts['autosave'] = True



	

class MenuPreferences(QtGui.QWidget):
	'''
	The mainWindow preferences shown using fingerTabs
	'''
	sigClosed = QtCore.pyqtSignal()

	def __init__(self, win, parent=None):
		
		super(MenuPreferences, self).__init__(parent)
		self.window = win
		self.setWindowTitle('Preferences')
		self.resize(530,480)
		self.tabs = FingerTabWidget(self)
		self.tab_session = _TabSession(self)
		self.tabs.addTab(self.tab_session, 'Session')
	

	def show(self):
		for i in range(self.tabs.count()):
			try:
				self.tabs.widget(i).update()
			except AttributeError:
				pass
		QtGui.QWidget.show(self)


	def closeEvent(self, evt):
		self.sigClosed.emit()
		super(MenuPreferences, self).closeEvent(evt)


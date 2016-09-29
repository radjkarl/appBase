# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

from fancywidgets.pyQtBased.FingerTabWidget import AutoResizeFingerTabWidget



class MenuPreferences(QtGui.QWidget):
    '''
    The mainWindow preferences shown using fingerTabs
    '''

    def __init__(self, win, parent=None):
        
        super(MenuPreferences, self).__init__(parent)
        self.window = win
        self.setWindowTitle('Preferences')
        self.tabs = AutoResizeFingerTabWidget(self)
        self.resize(300,200)
        self.tabs.setFixedSize(300,200)
        self.tab_session = _TabSession(self)
        self.tabs.addTab(self.tab_session, 'Session')


    def show(self):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            try:
                w.update()
            except AttributeError:
                pass
        QtGui.QWidget.show(self)



class _TabSession(QtGui.QWidget):
    '''
    The fingerTab 'session' in the preferences widget
    '''
    def __init__(self, prefWindow):
        super(_TabSession, self).__init__()
        self.app = QtGui.QApplication.instance()

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
        
        l = QtGui.QHBoxLayout()
        l.addWidget(QtGui.QLabel('Show close dialog'))
        self.showCloseDialog = QtGui.QCheckBox()
        self.showCloseDialog.clicked.connect(
            lambda val: self.app.session.app_opts.__setitem__('showCloseDialog', val))
        l.addWidget(self.showCloseDialog)
        vlayout.addLayout(l)
        vlayout.addStretch()


    def update(self):
        if not self.app.session.opts['autosave']:
            self.slider.setSliderPosition(99)
            self._updateInterval(99, False)
        else:
            a = self.app.session.opts['autosaveIntervalMin']
            self.slider.setSliderPosition(a)
            self._updateInterval(a, False)
        self.maxSessions.setValue(self.app.session.opts['maxSessions'])

        self.showCloseDialog.setChecked(self.app.session.app_opts.opts['showCloseDialog'])


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
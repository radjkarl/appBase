from builtins import range
# -*- coding: utf-8 -*-

from qtpy import QtGui, QtPrintSupport, QtWidgets, QtCore

from fancywidgets.pyQtBased.FingerTabWidget import AutoResizeFingerTabWidget



class MenuPreferences(QtWidgets.QWidget):
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
        QtWidgets.QWidget.show(self)



class _TabSession(QtWidgets.QWidget):
    '''
    The fingerTab 'session' in the preferences widget
    '''
    def __init__(self, prefWindow):
        super(_TabSession, self).__init__()
        self.app = QtWidgets.QApplication.instance()

        vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(vlayout)
        
        qtrecPrefs = QtWidgets.QGroupBox("Record Activity")
        qtrecLayout = QtWidgets.QVBoxLayout()
        qtrecPrefs.setLayout(qtrecLayout)
        vlayout.addWidget(qtrecPrefs)

        l = QtWidgets.QHBoxLayout()
        l.addWidget(QtWidgets.QLabel('max. saved states'))
        self.maxSessions = QtWidgets.QSpinBox()
        self.maxSessions.setRange(1,1000)
        self.maxSessions.valueChanged.connect(
            lambda val: self.app.session.opts.__setitem__('maxSessions', val))
        l.addWidget(self.maxSessions)
        qtrecLayout.addLayout(l)
        
        self.interval = QtWidgets.QLabel()
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation(1), self)#1...horizontal
        self.slider.sliderMoved.connect(self._updateInterval)
        
        qtrecLayout.addWidget(self.interval)
        qtrecLayout.addWidget(self.slider)
        
        l = QtWidgets.QHBoxLayout()
        l.addWidget(QtWidgets.QLabel('Show close dialog'))
        self.showCloseDialog = QtWidgets.QCheckBox()
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
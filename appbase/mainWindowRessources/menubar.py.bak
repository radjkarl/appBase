# -*- coding: utf-8 -*-

#foreign
from PyQt4 import QtGui

#this pgk
from menupreferences import MenuPreferences
from menuabout import MenuAbout
from menuShortcuts import MenuShortcuts

#own
from fancywidgets.pyQtBased.MenuBar import MenuBar as FWMenuBar
from fancytools.os.PathStr import PathStr


class _RenameStateDialog(QtGui.QDialog):
    '''
    A simple QDialog asking for a new name for a given save state
    '''
    def __init__(self, oldStateName):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle('Rename State')
        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        hl = QtGui.QHBoxLayout()
        hl.addWidget(QtGui.QLabel(oldStateName))
        self.editor = QtGui.QLineEdit(oldStateName)
        hl.addWidget(self.editor)
        
        l.addLayout(hl)
        
        self.btn_done = QtGui.QPushButton('Done')
        self.btn_done.clicked.connect(self.accept)
        l.addWidget(self.btn_done) 



class MenuBar(FWMenuBar):
    '''
    MenuBar including 
    * File (Save, Load, New...)
    * State (Next, Previous...)
    * View (Fullscreen)
    * Help (Shortcuts, About)
    '''
    
    def __init__(self):
        super(MenuBar, self).__init__()
        self.app = QtGui.QApplication.instance()
        #MENU - FILE
        self.menu_file = self.addMenu('&File')
        new_add = self.menu_file.addAction('New')
        new_add.setStatusTip('...in new window')
        new_add.setShortcuts(QtGui.QKeySequence.New)

        self.menu_file.addSeparator()

        save = self.menu_file.addAction('Save')
        save.setStatusTip('Override last saved session')
        save.setShortcuts(QtGui.QKeySequence.Save)
        save_as = self.menu_file.addAction('Save As')
        save.setStatusTip('Choose a name')
        save_as.setShortcuts(QtGui.QKeySequence.SaveAs)

        open_add = self.menu_file.addAction('Open')
        open_add.setStatusTip('...in new window')
        open_add.setShortcuts(QtGui.QKeySequence.Open)

        self.m_open_recent = self.menu_file.addMenu('Open Recent')
        self.m_open_recent.aboutToShow.connect(self._updateOpenRecentMenu)

        self.menu_file.addSeparator()
        self.file_preferences = MenuPreferences(self)
        self.menu_file.action_preferences = self.menu_file.addAction('Preferences')
        self.menu_file.action_preferences.triggered.connect(self.file_preferences.show)

        self.menu_file.addAction('Exit').triggered.connect(self.app.closeAllWindows)

        #MENU - STATE
        menu_state = self.addMenu('&State')
        self.a_previous = menu_state.addAction('Previous')
        self.a_previous.setStatusTip('Restore a previously saved state')
        self.a_previous.triggered.connect(self.app.session.restorePreviousState)

        self.a_next = menu_state.addAction('Next')
        self.a_next.setStatusTip('Restore a previously saved state')
        self.a_next.triggered.connect(self.app.session.restoreNextState)

        self.m_setState = menu_state.addMenu('Set')
        self.m_setState.aboutToShow.connect(self._updateSetStateActions)
        self.m_renameState = menu_state.addMenu('Rename')
        self.m_renameState.aboutToShow.connect(self._updateRenameStateActions)

        #MENU - VIEW
        self.menu_view = self.addMenu('&View')
        self.ckBox_fullscreen =  QtGui.QAction('Fullscreen', self.menu_view, checkable=True)
        self.menu_view.addAction(self.ckBox_fullscreen)
        self.ckBox_fullscreen.setStatusTip('Toggle between window and fullscreen')
        self.ckBox_fullscreen.triggered.connect(self.setFullscreen)
        self.ckBox_fullscreen.setShortcuts(QtGui.QKeySequence('F11'))

        #MENU - HELP
        self.menu_help = self.addMenu('&Help')
        
        sc = self.menu_help.addAction('Shortcuts')
        sc.setStatusTip('...list all shortcuts')
        self.shortcutsWidget = MenuShortcuts()
        sc.triggered.connect(self.shortcutsWidget.show)
        self.menu_help.addSeparator()

        about = self.menu_help.addAction('About')
        about.setShortcuts(QtGui.QKeySequence('F1'))
        self.aboutWidget = MenuAbout()
        about.triggered.connect(self.aboutWidget.show)

        #CONNECTING TO APPLICATION.SESSION
        s = self.app.session
        new_add.triggered.connect(s.new)
        save.triggered.connect(s.save)
        save_as.triggered.connect(lambda checked: s.saveAs())
        open_add.triggered.connect(s.open)


    def _updateOpenRecentMenu(self):
        self.m_open_recent.clear()
        for s in self.app.session.app_opts['recent sessions']:
            s = PathStr(s)
            a = self.m_open_recent.addAction(s.basename())
            a.setToolTip(s)
            a.triggered.connect(lambda checked, s=s: self.app.session.new(s))


    def _updateRenameStateActions(self):
        self.m_renameState.clear()
        se = self.app.session
        for s in se.stateNames():
            txt = '[%s]' %s
            if s == se.current_session:
                txt += ' <-'
            self.m_renameState.addAction(txt).triggered.connect(
                            lambda checked, s=s: self._showRenameStateDialog(s))


    def _showRenameStateDialog(self, oldStateName):
        r = _RenameStateDialog(oldStateName)
        ret = r.exec_()
        t = str(r.editor.text())
        if ret == QtGui.QDialog.Accepted and t and t != oldStateName:
            self.app.session.renameState(oldStateName, t)


    def _updateSetStateActions(self):
        self.m_setState.clear()
        se = self.app.session
        for s in se.stateNames():
            txt = '[%s]' %s
            if s == se.current_session:
                txt += ' <-'
            self.m_setState.addAction(txt).triggered.connect(
                            lambda checked, s=s: se.restoreStateName(s))


    def setFullscreen(self, fullscreen):
        '''toggle between fullscreen and normal window'''
        if not fullscreen:
            self.ckBox_fullscreen.setChecked(False)
            self.parent().showNormal()
        else:
            self.ckBox_fullscreen.setChecked(True)
            self.parent().showFullScreen()
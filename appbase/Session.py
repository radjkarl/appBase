# -*- coding: utf-8 -*-
import numpy as np

# from this pgk:
from appbase.Server import Server
from appbase.dialogs.FirstStart import FirstStart

# other own pgks:
from fancytools.os.PathStr import PathStr
from fancytools.utils.StreamSignal import StreamSignal
from fancytools.fcollections.naturalSorting import naturalSorting
from fancywidgets.pyQtBased.Dialogs import Dialogs

# foreign pkg:
import tempfile
import os
import sys
from distutils.spawn import find_executable
from zipfile import ZipFile
from time import gmtime, strftime
from PyQt4 import QtCore, QtGui
import cPickle as pickle

import __main__



class Session(QtCore.QObject):
    '''Session management to be accessible in QtGui.QApplication.instance().session

    * extract the opened (as pyz-zipped) session in a temp folder
    * create 2nd temp-folder for sessions to be saved
    * send a close signal to all child structures when exit
    * write a log file with all output
    * enable icons in menus of gnome-sessions [linux only]
    * gives option of debug mode
    '''

#     sigPathChanged = QtCore.pyqtSignal(object) #path
    sigSave = QtCore.pyqtSignal(object)        # state dict
    sigRestore = QtCore.pyqtSignal(object)     # state dict

    def __init__(self, args, **kwargs):
        """
        Args:
            first_start_dialog (Optional[bool]): 
                Show a different dialog for the first start.
            name (Optional[str]): The applications name.
            type (Optional[str]): The file type to be used for saving sessions.
            icon (Optional[str]): Path to the application icon.
        """

        QtCore.QObject.__init__(self)

        # SESSION CONSTANTS:
        self.NAME = kwargs.get('name', __main__.__name__)
        self.FTYPE = kwargs.get('ftype', 'pyz')
        self.ICON = kwargs.get('icon', None)
        # hidden app-preferences folder:
        self.dir = PathStr.home().mkdir('.%s' % self.NAME)
        self.APP_CONFIG_FILE = self.dir.join('config.txt')

        # session specific options:
        self.opts = _Opts({
                    'maxSessions': 3,
                    'enableGuiIcons': True,
                    'writeToShell': True,
                    'createLog': False,
                    'debugMode': False,
                    'autosave': True,
                    'autosaveIntervalMin': 15,
                    'server': False,
                     }, self)
        #global options - same for all new and restored sessions:
        self.app_opts = {'showCloseDialog':True, 'recent sessions':[]}

        if not self.APP_CONFIG_FILE.exists():
            #allow different first start dialog:
            dialog = kwargs.get('first_start_dialog', FirstStart)
            f = dialog(self)
            f.exec_()
            if not f.result():
                sys.exit()
            
            #create the config file
            with open(self.APP_CONFIG_FILE, 'w') as f:
                pass
        else:
            with open(self.APP_CONFIG_FILE,'r') as f:
                r = f.read()
                if r:
                    self.app_opts.update(eval(r))

        self._icons_enabled = False        
        self.log_file = None
        dirname = self.app_opts['recent sessions']
        if dirname:
            dirname = PathStr(dirname[-1]).dirname()
        self.dialogs = Dialogs(dirname)        
        self.saveThread = _SaveThread()
        
        self._createdAutosaveFile = None
        #make temp-dir
            #the directory where the content of the *pyz-file will be copied:
        self.tmp_dir_session = PathStr(tempfile.mkdtemp('%s_session' %self.NAME))
        self.tmp_dir_save_session = None
            #a work-dir for temp. storage:
        self.tmp_dir_work = PathStr(tempfile.mkdtemp('%s_work' %self.NAME))

        pathName = self._inspectArguments(args)
        
        self.setSessionPath(pathName)
        if self.opts['createLog']:
            self._setupLogFile()
        
        # create connectable stdout and stderr signal:
        self.streamOut = StreamSignal('out')
        self.streamErr = StreamSignal('err')
        self._enableGuiIcons()
        # Auto-save timer:
        self.timerAutosave = QtCore.QTimer()
        self.timerAutosave.timeout.connect(self._autoSave)

        self.opts.activate()
        #first thing to do after start:
        QtCore.QTimer.singleShot(0, self.restoreCurrentState)


    def setSessionPath(self, path, statename=None):
        if path: # and path.endswith('.%s' %self.FTYPE):
            # this script was opened out from a zip-container (named as '*.pyz')
            self.path = PathStr(path)

            self.dir = self.path.dirname().abspath()
            # extract the zip temporally
            ZipFile(self.path, 'r').extractall(path=self.tmp_dir_session)
            self.n_sessions = len(self.stateNames())
            # SET STATE
            snames = self.stateNames()
            if statename is None:
                # last one
                self.current_session = snames[-1]
            elif statename in snames:
                self.current_session = statename
            else:
                raise Exception("state '%s' not in saved states %s" %(statename, snames))
        else:
            self.path = None
            self.n_sessions = 0
            self.current_session = None


    def writeLog(self, write=True):
        if not self.log_file:
            return
        so = self.streamOut.message
        se = self.streamErr.message
        w = self.log_file.write
        if write:
            try:
                # ensure only connected once
                so.disconnect(w)
                se.disconnect(w)
            except TypeError:
                pass
            so.connect(w)
            se.connect(w)
        else:
            try:
                so.disconnect(w)
                se.disconnect(w)
            except TypeError:
                pass


    def _enableGuiIcons(self):
        # enable icons in all QMenuBars only for this program if generally disabled
        if self.opts['enableGuiIcons']:
            if os.name == 'posix':#linux
                this_env = str(os.environ.get('DESKTOP_SESSION'))
                relevant_env = ('gnome', 'gnome-shell', 'ubuntustudio', 'xubuntu')
                if this_env in relevant_env:
                    if 'false' in os.popen( 
                    #if the menu-icons on the gnome-desktop are disabled
                    'gconftool-2 --get /desktop/gnome/interface/menus_have_icons').read():
                        print 'enable menu-icons'
                        os.system(
                    'gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons True')
                        self._icons_enabled = True


    def _setupLogFile(self):
        lfile = self.tmp_dir_session.join('log.txt')
        if lfile.exists():
            self.log_file = open(lfile, 'a')
        else:
            self.log_file = open(lfile, 'w')
        self.log_file.write('''

####################################
New run at %s
####################################
            
''' %strftime( "%d.%m.%Y|%H:%M:%S", gmtime() ) )


    def checkMaxSessions(self, nMax=None):
        '''
        check whether max. number of saved sessions is reached
        if: remove the oldest session
        '''
        if nMax is None:
            nMax = self.opts['maxSessions']
        l = self.stateNames()
        if len(l) > nMax:
            for f in l[:len(l)-nMax]:
                self.tmp_dir_session.remove(str(f))


    def stateNames(self):
        """Returns:
             list: the names of all saved sessions
        """
        s = self.tmp_dir_session
        l = s.listdir()
        l = [x for x in l if s.join(x).isdir()]
        naturalSorting(l)
        # bring autosave to first position:
        if 'autoSave' in l:
            l.remove('autoSave')
            l.insert(0, 'autoSave')
        return l


    def restorePreviousState(self):
        s = self.stateNames()
        if s:
            i = s.index(self.current_session)
            if i > 1:
                self.current_session = s[i-1]
                self.restoreCurrentState()


    def restoreNextState(self):
        s = self.stateNames()
        if s:
            i = s.index(self.current_session)
            if i < len(s)-1:
                self.current_session = s[i+1]
                self.restoreCurrentState()


    def restoreStateName(self, name):
        '''restore the state of given [name]''' 
        self.current_session = name
        self.restoreCurrentState()


    def renameState(self, oldStateName, newStateName):
        s = self.tmp_dir_session.join(oldStateName)
        s.rename(newStateName)
        if self.current_session == oldStateName:
            self.current_session = newStateName
        print("==> State [%s] renamed to  [%s]" %(oldStateName, newStateName))


    def _recusiveReplacePlaceholderWithArray(self, state, arrays):
        def recursive(state):
            for key, val in state.items():
                if type(val) is dict:
                    recursive(val)
                elif type(val) is str and val.startswith('arr_'):
                    state[key] = arrays[val]
        recursive(state)


    def restoreCurrentState(self):
        if self.current_session:
            orig = self.tmp_dir_save_session
            path = self.tmp_dir_save_session = self.tmp_dir_session.join(
                                            self.current_session)
            with open( path.join('state.pickle'), "rb" ) as f:
                state = pickle.load( f )
            p = path.join('arrays.npz')
            if p.exists():
                arrays = np.load(path.join('arrays.npz'))
                self._recusiveReplacePlaceholderWithArray(state, arrays)

            self.dialogs.restoreState(state['dialogs'])
            self.opts.update(state['session'])
            self.sigRestore.emit(state)
            self.tmp_dir_save_session = orig
            
            print("==> State [%s] restored from '%s'" %(self.current_session, self.path))


    def addSession(self):
        self.current_session = self.n_sessions
        self.n_sessions += 1
        self.tmp_dir_save_session = self.tmp_dir_session.join(
                                        str(self.n_sessions)).mkdir()
        self.checkMaxSessions()


    def quit(self):
        print 'exiting...'
        # RESET ICONS
        if self._icons_enabled:
            print 'disable menu-icons'
            os.system( #restore the standard-setting for seeing icons in the menus
            'gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons False')

        # WAIT FOR PROMT IF IN DEBUG MODE
        if self.opts['debugMode']:
            raw_input("Press any key to end the session...")
        # REMOVE TEMP FOLDERS
        try:
            self.tmp_dir_session.remove()
            self.tmp_dir_work.remove()
        except OSError:
            pass  # in case the folders are used by another process

        with open(self.APP_CONFIG_FILE, 'w') as f:
            f.write(str(self.app_opts))
        # CLOSE LOG FILE
        if self.log_file:
            self.writeLog(False)
            self.log_file.close()


    def _inspectArguments(self, args):
        '''inspect the command-line-args and give them to appBase'''
        if args:
            self.exec_path = PathStr(args[0])
        else:
            self.exec_path = None

        session_name = None
        args = args[1:]
        
        openSession = False
        for arg in args:
            if arg in ('-h', '--help'):
                self._showHelp()
            elif arg in ('-d', '--debug'):
                print 'RUNNGING IN DEBUG-MODE'
                self.opts['debugMode'] = True
            elif arg in ('-l', '--log'):
                print 'CREATE LOG'
                self.opts['createLog'] = True
            elif arg in ('-s', '--server'):
                self.opts['server'] = True
            elif arg in ('-o', '--open'):
                openSession = True
            elif openSession:
                session_name = arg
            else:
                print "Argument '%s' not known." %arg
                return self._showHelp()
        return session_name


    def _showHelp(self):
        sys.exit('''
    %s-sessions can started with the following arguments:
        [-h or --help] - show the help-page
        [-d or --debug] - run in debugging-mode
        [-l or --log] - create log file
        [-n or --new] - start a new session, don'l load saved properties
        [-exec [cmd]] - execute python code from this script/executable
        ''' % self.__class__.__name__)


    def save(self):
        '''save the current session
        override, if session was saved earlier'''
        if self.path:
            self._saveState(self.path)
        else:
            self.saveAs()


    def saveAs(self, filename=None):
        if filename is None:
            # ask for filename:
            filename = self.dialogs.getSaveFileName(filter="*.%s" % self.FTYPE)
        if filename:
            self.path = filename
            self._saveState(self.path)
            if self._createdAutosaveFile:
                self._createdAutosaveFile.remove()
                print("removed automatically created '%s'" % self._createdAutosaveFile)
                self._createdAutosaveFile = None


    def replace(self, path):
        '''
        replace current session with one given by file path
        '''
        self.setSessionPath(path)
        self.restoreCurrentState()


    def open(self):
        '''open a session to define in a dialog in an extra window''' 
        filename = self.dialogs.getOpenFileName(filter="*.%s" % self.FTYPE)
        if filename:
            self.new(filename)


    def new(self, filename=None):
        '''start a session an independent process'''
        path = (self.exec_path,)
        if self.exec_path.filetype() in ('py', 'pyw', 'pyz', self.FTYPE):
            #get the absolute path to the python-executable
            p = find_executable("python")
            path = (p, 'python') + path
        else:
            #if run in frozen env (.exe):
            #first arg if execpath of the next session:
            path += (self.exec_path,)
        if filename:
            path += ('-o', filename)
        os.spawnl(os.P_NOWAIT, *path)


    def registerMainWindow(self, win):
        win.setWindowIcon(QtGui.QIcon(self.ICON))

        self._mainWindow = win
        win.show = self._showMainWindow
        win.hide = self._hideMainWindow
        if self.opts['server']:
            server_ = Server(win)
            win.hide()
        else:
            win.show()


    def _showMainWindow(self):
        try:
            #restore autosave
            del self._autosave
        except AttributeError:
            pass
        self._mainWindow.__class__.show(self._mainWindow)


    def _hideMainWindow(self):
        #disable autosave on hidden window
        self._autosave = self.opts['autosave']
        self.opts['autosave'] = False
        self._mainWindow.__class__.hide(self._mainWindow)


    def _saveState(self, path):
        '''save current state and add a new state'''
        self.addSession()#next session
        self._save(str(self.n_sessions), path)


    def _autoSave(self):
        '''save state into 'autosave' '''
        a = 'autoSave'
        path = self.path
        if not path:
            path= self.dir.join('%s.%s' %(a,self.FTYPE))
            self._createdAutosaveFile = path
        self.tmp_dir_save_session = self.tmp_dir_session.join(a).mkdir()
        self._save(a, path)


    def blockingSave(self, path):
        '''
        saved session to file - returns after finish
        only called by interactiveTutorial-save at the moment
        '''
        self.tmp_dir_save_session = self.tmp_dir_session.join('block').mkdir()
        state = {'session': dict(self.opts),
                 'dialogs': self.dialogs.saveState()}
        self.saveThread.prepare('0', path, self.tmp_dir_session, state)
        self.sigSave.emit(self)
        self.saveThread.run() 


    def _save(self, stateName, path):
        '''save into 'stateName' to pyz-path'''
        print('saving...')

        state = {'session': dict(self.opts),
                 'dialogs': self.dialogs.saveState()}

        self.sigSave.emit(state)
        self.saveThread.prepare(stateName, path, self.tmp_dir_session, state)
        self.saveThread.start()

        self.current_session = stateName

        r = self.app_opts['recent sessions']
        try:
            # is this session already exists: remove it
            r.pop(r.index(path))
        except ValueError:
            pass
        # add this session at the beginning
        r.insert(0,path)



class _SaveThread(QtCore.QThread):
    """Run the saving procedure in a thread to be non-blocking
    """

    def prepare(self, stateName, path, dirpath, state):
        self.stateName = stateName
        self.path = path
        self.dirpath = dirpath
        self._state = state


    def _recusiveReplaceArrayWithPlaceholder(self, state):
        '''
        replace all numpy.array within the state dict
        with a placeholder
        this allows to save the arrays extra using numpy.save_compressed
        ''' 
        c = 0
        arrays = {}
        
        def recursive(c, state):
            for key, val in state.iteritems():
                if type(val) is dict:
                    recursive(c, val)
                else:
                    if isinstance(val, np.ndarray):
                        name = 'arr_%i' %c
                        arrays[name] = val
                        state[key] = name
                        c += 1
        recursive(c, state)
        return arrays


    def run(self):
        arrays = self._recusiveReplaceArrayWithPlaceholder(self._state)
        # save state
        p = self.dirpath.mkdir(self.stateName)
        with open( p.join('state.pickle'), "wb" ) as f:
            pickle.dump( self._state, f )
        # save arrays
        if len(arrays):
            np.savez_compressed(p.join('arrays.npz'), **arrays)
        del self._state
        # create zip file
        with ZipFile(self.path,'w',
             # FROM https://docs.python.org/2/library/zipfile.html :
             # allowZip64 is True zipfile will create ZIP files 
             #  that use the ZIP64 extensions when the zipfile is larger than 2 
             # GB. If it is false (the default) zipfile will raise an exception 
             # when the ZIP file would require ZIP64 extensions. ZIP64 extensions are 
             # disabled by default because the default zip and unzip commands on Unix 
             # (the InfoZIP utilities) don’t support these extensions.
             allowZip64=True) as zipFile:

            # copy a dir to the zip-file:
            basedir = self.dirpath
            for root, _, files in os.walk(self.dirpath):
                dirname = root.replace(basedir, '')
                for f in files:
                    zipFile.write( os.path.join(root,f), os.path.join(dirname,f) )

        print("|%s| ==> State [%s] saved to '%s'" %(
                    strftime("%H:%M:%S", gmtime()),
                    self.stateName, self.path))



class _Opts(dict):
    '''session.opts dictionary
     -> execute things when opts are changed
    '''
    def __init__(self, d, session):
        dict.__init__(self, d)
        self.session = session
        self._activated = False


    def activate(self):
        self._activated = True
        self.update(self)


    def update(self, d):
        for key, val in d.iteritems():
            self.__setitem__(key, val)


    def __setitem__(self, item, value):
        if self._activated:
            if item == 'writeToShell':
                self.session.streamOut.setWriteToShell(value)
                self.session.streamErr.setWriteToShell(value)
            elif item == 'createLog':
                if value: 
                    self.session.writeLog(value)
            elif item == 'autosaveIntervalMin':
                self.session.timerAutosave.setInterval(value*60*1000)
            elif item == 'autosave':
                t = self.session.timerAutosave
                if not t.isActive() and value:
                    t.start()
                elif t.isActive() and not value:
                    t.stop()
            elif item == 'maxSessions':
                self.session.checkMaxSessions(value)

        return dict.__setitem__(self, item, value)
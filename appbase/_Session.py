# -*- coding: utf-8 -*-


#from this pgk:
import appbase
from appbase.Launcher import Launcher
from appbase.Server import Server

#other own pgks:
from fancytools.os.PathStr import PathStr
from fancytools.os.legalizeFilename import legalizeFilename
from fancytools.utils.StreamSignal import StreamSignal
from fancytools.fcollections.naturalSorting import naturalSorting
from fancywidgets.pyQtBased.Dialogs import Dialogs

#foreign pkg:
import tempfile
import os
import sys
import shutil
import distutils
from zipfile import ZipFile
from time import gmtime, strftime
from PyQt4 import QtCore
import pprint


class _Opts(dict):
    def __init__(self, d, session):
        dict.__init__(self, d)
        self.session = session
        self._fn_write_log = None
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

            elif item == 'createLog':
                if value:  
                    if not self._fn_write_log:
                        self._fn_write_log = lambda val: self.session.log_file.write(val)
                        #connect those to different addText-methods
                        self.session.streamOut.message.connect(self._fn_write_log)
                        self.session.streamErr.message.connect(self._fn_write_log)                
                elif self._fn_write_log:
                    #connect those to different addText-methods
                    self.session.streamOut.message.disconnect(self._fn_write_log)
                    self.session.streamErr.message.disconnect(self._fn_write_log)  
    
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




class Session(QtCore.QObject):
    '''
    * extract the opened (as pyz-zipped) session in a temp folder
    * create 2nd temp-folder for sessions to be saved
    * send a close signal to all child structures when exit
    * write a log file with all output
    * enable icons in menues of gnome-sessions
    * gives option of debug mode
    '''

    sigPathChanged = QtCore.pyqtSignal(object) #path
    sigSave = QtCore.pyqtSignal(object)        #save-dir
    sigRestore = QtCore.pyqtSignal(object)     #restore-dir

    def __init__(self, args):
        QtCore.QObject.__init__(self)
        
        self.opts = _Opts({
                    'maxSessions':10,
                    'enableGuiIcons':True,
                    'writeToShell':True,
                    'createLog':True,
                    'debugMode':False,
                    'autosave':True,
                    'autosaveIntervalMin':15,
                    'showCloseDialog':True,
                    'server':False,
                     }, self)
        
        self._icons_enabled = False        
        self.log_file = None
        self.dialogs = Dialogs()
        self._createdAutosaveFile = None
        #make temp-dir
            #the directory where the content of the *pyz-file will be copied:
        self.tmp_dir_session = PathStr(tempfile.mkdtemp('%s_session' %__name__))
        self.tmp_dir_save_session = None
            #a work-dir for temp. storage:
        self.tmp_dir_work = PathStr(tempfile.mkdtemp('%s_work' %__name__))

        pathName = self._inspectArguments(args)
        
        self.setSessionPath(pathName)
        
        self._setupLogFile()
        
        # create connectable stdout and stderr signal:
        self.streamOut = StreamSignal('out')
        self.streamErr = StreamSignal('err')
        self._enableGuiIcons()
        path= self.dir.join('autoSave.pyz')
        #Timer
        self.timerAutosave = QtCore.QTimer()
        self.timerAutosave.timeout.connect(self._autoSave)

        self.opts.activate()
        

    def setSessionPath(self, path, statename=None):
        if path.endswith('.pyz'):
            # this script was opened out from a zip-container (named as '*.pyz')
            self._path = PathStr(path)
            self.dir = self._path.dirname().abspath()
            # extract the zip temporally
            ZipFile(self._path,'r').extractall(path=self.tmp_dir_session)
            self.n_sessions = len(self.stateNames()) 
            #SET STATE
            snames = self.stateNames()
            if statename == None:
                #last one
                self.current_session = snames[-1]
            elif statename in snames:
                self.current_session = statename
            else:
                raise Exception("state '%s' not in saved states %s" %(statename, snames))
            
        else:
            self.dir = Launcher.rootDir()
            self._path = None
            self.n_sessions = 0
            self.current_session = None
            #self._createStarter()


   # def _createStarter(self):
     #   pass
#         content = '''
#         from PyQt4 import QtGui
#         '''
#         self.addContentToSave(self, content, '__main__.py')
#         
#                 if not self.tmp_dir_save_session.join('__main__.py').exists():
#             #because opened from regular .py
#             self.addFileToSave(__main__.__file__, '__main__.py')


    def _enableGuiIcons(self):
        #enable icons in all QMenuBars only for this program if generally disabled
        if self.opts['enableGuiIcons']:
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
        if nMax == None:
            nMax = self.opts['maxSessions']
        l = self.stateNames()
        if len(l) > nMax:
            for f in l[:len(l)-nMax]:
                self.tmp_dir_session.remove(str(f))


    def stateNames(self):
        '''
        return the names of all saved sessions
        '''
        s = self.tmp_dir_session
        l = s.listdir()
        l = [x for x in l if s.join(x).isdir()]
        naturalSorting(l)
        return l


    def restorePreviousState(self):
        s = self.stateNames()
        i = s.index(self.current_session)
        if i > 0:
            self.current_session = s[i-1]
            self.restoreCurrentState()
       
             
    def restoreNextState(self):
        s = self.stateNames()
        i = s.index(self.current_session)
        if i < len(s):
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
        print "==> State [%s] renamed to  [%s]" %(oldStateName, newStateName)


    def restoreCurrentState(self):
        if self.current_session:
            orig = self.tmp_dir_save_session
            self.tmp_dir_save_session = self.tmp_dir_session.join(
                                            self.current_session)
            self.opts.update(eval(self.getSavedContent('session.txt')))
            self.sigRestore.emit(self)
            self.tmp_dir_save_session = orig           
            print "==> State [%s] restored from '%s'" %(self.current_session, self.tmp_dir_session)


    def addSession(self):
        self.current_session = self.n_sessions
        self.n_sessions += 1

        self.tmp_dir_save_session = self.tmp_dir_session.join(
                                        str(self.n_sessions)).mkdir()
        
        #self._setupLogFile()
        self.checkMaxSessions()
       
#         
#                 #create new log-filename
#         logFolder = self.tmp_dir_save_session.join('log')
#         d = logFolder.listdir()
#         if d:
#             d.sort()
#         ####raus
#             #...as last log-number +1
#             logfilename = logFolder.join( '%s.log' %str(int(d[-1][:-4]) + 1 ))
#             #save only the last MAX_N_LOG_FILES
#             for f in d[MAX_N_LOG_FILES:]:
#                 logFolder.remove(f)
#         else:
#             logfilename = logFolder.join('1.log')
# 
#         #create new save-filename
#         savefolder = self.tmp_dir_save_session.join('save')
#         d = savefolder.listdir()
# 
#         QtRec.log_file_name = self.tmp_dir_work.join('save.py')
#         if d:
#             d.sort()
#             #...as last save-number +1
#             self._save_file_name = savefolder.join( '%s.py' %str(int(d[-1][:-3]) + 1 ))
#             #create one singe file form all saved ones
#             with open(QtRec.core.log_file_name, "wb") as outfile:
#                 for f in d:
#                     with open(savefolder.join(f), "rb") as infile:
#                         outfile.write(infile.read())
#         else:
#             #save empty
#             self._save_file_name = savefolder.join('1.py')



    def createSavePath(self, *fileNames):
        '''create a file-path within the saved sessions temp folder
        if not already existent'''
        path = self.tmp_dir_save_session
        for s in fileNames[:-1]:
            path = path.join(s).mkdir()
        return path.join(fileNames[-1])


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


    def addContentToSave(self, content, *path):
        '''write content to save to the file path 
        given by [*path]'''
        path = self.createSavePath(*path)
        with file(path,'w') as f:
#             if isinstance(content, np.ndarray):
#                 np.save(f, content)
            if isinstance(content, QtCore.QString):
                f.write(unicode(content))
            elif isinstance(content, basestring):
                f.write(content)
            else: 
                pp = pprint.PrettyPrinter(indent=4)
                f.write(pp.pformat(content))


    def getSavedFile(self,*path):
        '''return the absolute file path within the temp folder for saved sessions'''
        if self.tmp_dir_save_session:
            t = self.tmp_dir_save_session.join(*path)
            if t.exists():
                return t


    def getSavedContent(self,*path):
        '''open the file given by [*path] and return its content'''
        t = self.getSavedFile(*path)
        if t:
            with open(t,'r') as content:
                return content.read()


    @property
    def path(self):
        '''return the path of the saved session, like
        /home/USER/.../test.pyz'''
        return self._path


    @path.setter
    def path(self, name):
        self._path = name
        self.sigPathChanged.emit(name)


    def quit(self):
        print 'exiting...'
        #RESET ICONS
        if self._icons_enabled:
            print 'disable menu-icons'
            os.system( #restore the standard-setting for seeing icons in the menus
            'gconftool-2 --type Boolean --set /desktop/gnome/interface/menus_have_icons False')

        #WAIT FOR PROMT IF IN DEBUG MODE
        if self.opts['debugMode']:
            raw_input("Press any key to end the session...")
        #REMOVE TEMP FOLDERS
        try:
            self.tmp_dir_session.remove()
            self.tmp_dir_work.remove()
        except OSError:
            pass #in case the folders are used by another process
        #CLOSE LOG FILE
        if self.log_file:
            self.log_file.close()


    def _inspectArguments(self, args):
        '''inspect the command-line-args and give them to appBase'''
        self.exec_path = PathStr(args[0])
        d = os.path.dirname(self.exec_path)
        if d and appbase.__path__[0].startswith(d): #executed from installpath
            progName = os.path.basename(self.exec_path)
            folder = Launcher.rootDir()

            projectName = folder.join(progName)
        else:
            projectName = self.exec_path
        args = args[1:]
        
        openSession = False
        for arg in args:
            if arg in ('-h','--help'):
                self._showHelp()
            elif arg in ('-d','--debug'):
                print 'RUNNGING IN DEBUG-MODE'
                self.opts['debugMode'] = True
            elif arg in ('-l','--nolog'):
                print 'CREATE NO LOG'
                self.opts['createLog'] = False
            elif arg in ('-s', '--server'):
                self.opts['server'] = True
            elif arg in ('-o','--o'):
                openSession = True
            elif openSession:
                projectName = arg
            else:
                print  "Argument '%s' not known." %arg
                return self._showHelp()
        return projectName


    def _showHelp(self):
        sys.exit('''
    %s-sessions can started with the following arguments:
        [-h or --help] - show the help-page
        [-d or --debug] - run in debuging-mode
        [-l or --nolog] - create no log file
        [-n or --new] - start a new session, don'l load saved properties
        ''' %self.__class__.__name__)


    def save(self):
        '''save the current session
        override, if session was saved earlier'''
        if self._path:
            self._saveState(self._path)
        else:
            self.saveAs()


    def saveAs(self, filename=None):
        if filename == None:
            #ask for filename:
            filename = self.dialogs.getSaveFileName(filter="*.pyz")
        if filename:
            self.path = filename
            self._saveState(self.path)
            if self._createdAutosaveFile:
                self._createdAutosaveFile.remove()
                print "removed automatically created '%s'" %self._createdAutosaveFile
                self._createdAutosaveFile = None
                

    def open(self):
        '''open a session to define in a dialog in an extra window''' 
        filename = self.dialogs.getOpenFileName(filter="*.pyz")
        if filename:
            self.new(filename)


    def new(self, filename=None):
        '''start a session an independent process'''
        path = (self.exec_path,)
        if self.exec_path.filetype() in ('py', 'pyw', 'pyz'):
            #get the absolute path to the python-executable
            p = distutils.spawn.find_executable("python")
            path = (p, 'python') + path
        else:
            #for some reason the first arg is ignored in spawnv -> set a dummy arg
            path += ('DUMMY',)
        if filename:
            path += ('-o', filename)
        #print path, 876786
        os.spawnl(os.P_NOWAIT, *path)
 

    def registerMainWindow(self, win):
        self._mainWindow = win
        win.show = self._showMainWindow
        win.hide = self._hideMainWindow
        if self.opts['server']:
            server = Server(win)
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


    def _saveDir(self, dirpath):
        '''copy a dir to the zip-file'''
        basedir = dirpath
        for root, dirs, files in os.walk(dirpath):
            dirname = root.replace(basedir, '')
            for f in files:
                self._zipFile.write( os.path.join(root,f), os.path.join(dirname,f) )


    def _saveState(self, path):
        '''save current state and add a new state'''
        self.addSession()#next session
        self._save(str(self.n_sessions), path)



    def _autoSave(self):
        '''save state into 'autosave' '''
        a = 'autoSave'
        path = self._path
        if not path:
            path= self.dir.join('%s.pyz' %a)
            self._createdAutosaveFile = path
        self.tmp_dir_save_session = self.tmp_dir_session.join(a).mkdir()
        self._save(a, path)
        

    def _save(self, stateName, path):
        '''save into 'stateName' to pyz-path'''
        self.addContentToSave(self.opts, 'session.txt')
        self.sigSave.emit(self)
        with ZipFile(path,'w') as self._zipFile:
            self._saveDir(self.tmp_dir_session)
        self.current_session = stateName
        print "==> State [%s] saved to '%s'" %(stateName, path)
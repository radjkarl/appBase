import sys, os

from PyQt4 import QtGui


from fancytools.os.isAdmin import isAdmin
from fancytools.os.PathStr import PathStr
from fancytools.os.StartMenuEntry import StartMenuEntry
from fancytools.os.runAsAdmin import runAsAdmin
from fancytools.os.assignFtypeToPyFile import assignFtypeToPyFile

import __main__



class FirstStart(QtGui.QDialog):
    '''
    Dialog to ask user to embed the application into the OS
    '''
    def __init__(self, session):
        QtGui.QDialog.__init__(self)
        
        self.name =  session.NAME
        self.ftype = session.FTYPE
        self.icon = session.ICON

        self.setWindowTitle('Starting %s the first time...' %self.name)
        self.resize(300,100)

        l = QtGui.QVBoxLayout()
        self.setLayout(l)

        self.cb_startmenu = QtGui.QCheckBox('Add to start menu')
        self.cb_startmenu.setChecked(True)
        self.cb_mime = QtGui.QCheckBox('Open *.%s files with %s [NEEDS ADMIN]' %(self.ftype, self.name))
        self.cb_mime.setChecked(True)

        self.btn_done = QtGui.QPushButton('Done')
        self.btn_done.clicked.connect(self.accept)

        l.addWidget(QtGui.QLabel("The folder '.%s' will be created in \nyour home directory to store all\nnecassary information." %self.name)) 

        l.addWidget(self.cb_startmenu) 
        l.addWidget(self.cb_mime) 
        l.addWidget(self.btn_done) 


    def accept(self, evt):
        '''
        write setting to the preferences
        '''
        # determine if application is a script file or frozen exe (pyinstaller)
        frozen = getattr(sys, 'frozen', False)
        if frozen:
            app_file = sys.executable
        else:
            app_file = PathStr(__main__.__file__).abspath()

        if self.cb_startmenu.isChecked():
            #TODO: allow only logo location 
            #icon = app_file.dirname().join('media', 'logo.ico')
            StartMenuEntry(self.name, app_file, icon=self.icon, 
                           console=False).create()
        
        if self.cb_mime.isChecked():
            #get admin rights
            if not isAdmin():
                try:
                    #run this file as __main__ with admin rights:
                    if frozen:
                        cmd = "from %s import embeddIntoOS\nembeddIntoOS('%s', '%s', '%s')"%(__name__, '', self.ftype ,self.name)
                        # in this case there is no python.exe and no moduly.py to call
                        # thats why we have to import the method and execute it
                        runAsAdmin((sys.executable, '-exec', cmd))
                    else:
                        runAsAdmin((sys.executable, __file__, app_file, self.ftype ,self.name))
                except:
                    print 'needs admin rights to work'
            else:
                embeddIntoOS(app_file, self.ftype, self.name)
        
        QtGui.QDialog.accept(self)
        
  
        
#RUN THIS AS ADMIN PROCESS!
def embeddIntoOS(app_file, ftype, app_name):
    if app_file:
        args = (app_file,  '-o')
    else:
        args = '-o'
    assignFtypeToPyFile(ftype, args, mimetype='%s.file' %app_name, showTerminal=False)
    


if __name__ == '__main__':
    try:
        embeddIntoOS(*sys.argv[1:])
    except Exception, err:
        print err
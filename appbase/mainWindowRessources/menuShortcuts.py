from PyQt4 import QtGui


class MenuShortcuts(QtGui.QWidget):
    '''
    Window showing the application shortcuts
    '''
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle('Shortcuts')
        
        l = QtGui.QGridLayout()
        self.setLayout(l)
        lk = QtGui.QLabel('<b>Key</b>')
        ld = QtGui.QLabel('<b>Description</b>')
        l.addWidget(lk,0,0)
        l.addWidget(ld,0,1)

        line = QtGui.QFrame(self)
        line.setLineWidth(2)
        line.setMidLineWidth(1)
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Raised)
        l.addWidget(line, 1, 0, 1, 2)
        
        self._r = 2

  
    def addShortcut(self, key, description):
        lk = QtGui.QLabel(key)
        ld = QtGui.QLabel(description)
        l = self.layout()
        l.addWidget(lk,self._r,0)
        l.addWidget(ld,self._r,1)     
        self._r += 1 
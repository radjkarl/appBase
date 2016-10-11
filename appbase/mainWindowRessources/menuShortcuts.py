from qtpy import QtWidgets


class MenuShortcuts(QtWidgets.QWidget):
    '''
    Window showing the application shortcuts
    '''

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Shortcuts')

        l = QtWidgets.QGridLayout()
        self.setLayout(l)
        lk = QtWidgets.QLabel('<b>Key</b>')
        ld = QtWidgets.QLabel('<b>Description</b>')
        l.addWidget(lk, 0, 0)
        l.addWidget(ld, 0, 1)

        line = QtWidgets.QFrame(self)
        line.setLineWidth(2)
        line.setMidLineWidth(1)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Raised)
        l.addWidget(line, 1, 0, 1, 2)

        self._r = 2

    def addShortcut(self, key, description):
        lk = QtWidgets.QLabel(key)
        ld = QtWidgets.QLabel(description)
        l = self.layout()
        l.addWidget(lk, self._r, 0)
        l.addWidget(ld, self._r, 1)
        self._r += 1

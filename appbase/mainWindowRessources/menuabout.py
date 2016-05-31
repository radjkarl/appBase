# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSvg



class MenuAbout(QtGui.QWidget):
    """Create a simple about window, showing a logo

    and general information defined in the main modules __init__.py file
    """
    def __init__(self, parent=None):
        self.app = QtGui.QApplication.instance()

        super(MenuAbout, self).__init__(parent)
        self.setWindowTitle('About')

        l = QtGui.QHBoxLayout()
        self.setLayout(l)
        logo = QtSvg.QSvgWidget(self.app.session.ICON)
        s = logo.sizeHint()
        aR = float(s.height()) / s.width()
        h = 150
        w = h/aR
        logo.setFixedSize(w, h)
        self.label_txt = QtGui.QLabel()

        l.addWidget(logo)
        l.addWidget(self.label_txt)


    def setModule(self, mod):
        '''
        fill the about about label txt with the module attributes of the module
        '''
        txt = """<b>%s</b> - %s<br><br>
Author:        %s<br>
Email:        %s<br>
Version:        %s<br>
License:        %s<br>
Url:            <a href="%s">%s</a>""" % (
                        mod.__name__,
                        mod.__doc__,
                        mod.__author__,
                        mod.__email__,
                        mod.__version__,
                        mod.__license__,
                        mod.__url__, mod.__url__)
        self.label_txt.setText(txt)
        self.label_txt.setOpenExternalLinks(True)


    def setInstitutionLogo(self, path):
        logo = QtSvg.QSvgWidget(path)
        s = logo.sizeHint()
        aR = float(s.height()) / s.width()
        h = 150
        w = h/aR
        logo.setFixedSize(int(w), int(h))
        self.layout().addWidget(logo)

# -*- coding: utf-8 -*-
from qtpy import QtWidgets, QtSvg, QtGui, QtCore


class MenuAbout(QtWidgets.QWidget):
    """Create a simple about window, showing a logo

    and general information defined in the main modules __init__.py file
    """

    def __init__(self, parent=None):
        self.app = QtWidgets.QApplication.instance()

        super(MenuAbout, self).__init__(parent)
        self.setWindowTitle('About')

        l = QtWidgets.QHBoxLayout()
        self.setLayout(l)
        logo = QtSvg.QSvgWidget(self.app.session.ICON)
        s = logo.sizeHint()
        aR = s.height() / s.width()
        h = 150
        w = h / aR
        logo.setFixedSize(w, h)
        self.label_txt = QtWidgets.QLabel()

        l.addWidget(logo)
        l.addWidget(self.label_txt)

    def setModule(self, mod):
        """
        fill the about about label txt with the module attributes of the module
        """
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

    def setInstitutionLogo(self, pathList: tuple):
        """
        takes one or more [logo].svg paths
            if logo should be clickable, set
                pathList = (
                (my_path1.svg,www.something1.html),
                (my_path2.svg,www.something2.html),
                ...)
        """
        for p in pathList:
            url = None
            if type(p) in (list, tuple):
                p, url = p
            logo = QtSvg.QSvgWidget(p)
            s = logo.sizeHint()
            aR = s.height() / s.width()
            h = 150
            w = h / aR
            logo.setFixedSize(int(w), int(h))
            self.layout().addWidget(logo)
            if url:
                logo.mousePressEvent = lambda evt, u=url: self._openUrl(evt, u)

    def _openUrl(self, evt, url):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        return evt.accept()

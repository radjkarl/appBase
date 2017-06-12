# coding=utf-8
from __future__ import print_function
from builtins import str
# -*- coding: utf-8 -*-

###############
# The launcher class is not updated any more
# I might remove it
###############

# own
import appbase
from fancytools.os.PathStr import PathStr
from fancywidgets.pyQtBased.Dialogs import Dialogs

# foreign
from qtpy import QtGui, QtWidgets, QtCore, QtSvg

# built-in
import os
from zipfile import ZipFile
import distutils
from distutils import spawn
import subprocess
import sys
import tempfile


CONFIG_FILE = PathStr.home().join(__name__)


class Launcher(QtWidgets.QMainWindow):
    """
    A graphical starter for *.pyz files created by the save-method from
    appbase.MainWindow

    NEEDS AN OVERHAUL ... after that's done it will be able to:

    * show all *.pyz-files in a filetree
    * show the session specific ...

        * icon
        * description
        * author etc.
    * start, remove, rename, modify a session
    * modify, start a certain state of a session
    """

    def __init__(self,
                 title='PYZ-Launcher',
                 icon=None,
                 start_script=None,
                 left_header=None,
                 right_header=None,
                 file_type='pyz'
                 ):
        self.dialogs = Dialogs()

        _path = PathStr.getcwd()
        _default_text_color = '#3c3c3c'

        if icon is None:
            icon = os.path.join(_path, 'media', 'launcher_logo.svg')
        if start_script is None:
            start_script = os.path.join(_path, 'test_session.py')
        if left_header is None:
            _description = "<a href=%s style='color: %s'>%s</a>" % (
                appbase.__url__, _default_text_color, appbase.__doc__)

            left_header = """<b>%s</b><br>
                version&nbsp;&nbsp;
                <a href=%s style='color: %s'>%s</a><br>
                autor&nbsp;&nbsp;&nbsp;&nbsp;
                    <a href=mailto:%s style='color: %s'>%s</a> """ % (  # text-decoration:underline
                _description,
                os.path.join(_path, 'media', 'recent_changes.txt'),
                _default_text_color,
                appbase.__version__,
                appbase.__email__,
                _default_text_color,
                appbase.__author__
            )
        if right_header is None:
            # if no header is given, list all pdfs in folder media as link
            d = _path
            right_header = ''
            for f in os.listdir(os.path.join(d, 'media')):
                if f.endswith('.pdf'):
                    _guidePath = os.path.join(d, 'media', f)
                    right_header += "<a href=%s style='color: %s'>%s</a><br>" % (
                        _guidePath, _default_text_color, f[:-4])
            right_header = right_header[:-4]

        QtWidgets.QMainWindow.__init__(self)

        self._start_script = start_script
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(icon))
        self.resize(900, 500)
        # BASE STRUTURE
        area = QtWidgets.QWidget()
        self.setCentralWidget(area)
        layout = QtWidgets.QVBoxLayout()
        area.setLayout(layout)
        #header = QtWidgets.QHBoxLayout()
        # layout.addLayout(header)
        # grab the default text color of a qlabel to color all links from blue to it:
        # LEFT TEXT
        info = QtWidgets.QLabel(left_header)
        info.setOpenExternalLinks(True)
        # LOGO
        header = QtWidgets.QWidget()
        header.setFixedHeight(70)
        headerlayout = QtWidgets.QHBoxLayout()
        header.setLayout(headerlayout)
        logo = QtSvg.QSvgWidget(icon)
        logo.setFixedWidth(50)
        logo.setFixedHeight(50)
        headerlayout.addWidget(logo)
        headerlayout.addWidget(info)
        layout.addWidget(header)
        # RIGHT_HEADER
        userGuide = QtWidgets.QLabel(right_header)
        userGuide.setOpenExternalLinks(True)
        userGuide.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        headerlayout.addWidget(userGuide)
        # ROOT-PATH OF THE SESSIONS
        rootLayout = QtWidgets.QHBoxLayout()
        rootFrame = QtWidgets.QFrame()
        rootFrame.setFrameStyle(
            QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
        rootFrame.setFixedHeight(45)
        rootFrame.setLineWidth(0)
        rootFrame.setLayout(rootLayout)
        layout.addWidget(rootFrame)
        self.rootDir = QtWidgets.QLabel()
        self.rootDir.setAutoFillBackground(True)
        self.rootDir.setStyleSheet("QLabel { background-color: white; }")

        # FILE-BROWSER
        self.treeView = _TreeView()

        self.fileSystemModel = _FileSystemModel(self.treeView, file_type)
        self.fileSystemModel.setNameFilters(['*.%s' % file_type])
        self.fileSystemModel.setNameFilterDisables(False)
        self.treeView.setModel(self.fileSystemModel)

        treelayout = QtWidgets.QHBoxLayout()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation(1))

        self.fileInfo = _PyzInfo(splitter, self.fileSystemModel, self.treeView)
        self.treeView.clicked.connect(self.fileInfo.update)

        splitter.addWidget(self.treeView)
        splitter.addWidget(self.fileInfo)
        treelayout.addWidget(splitter)

        layout.addLayout(treelayout)

        # get last root-path
        self._path = PathStr('')
        if CONFIG_FILE:
            try:
                self._path = PathStr(
                    open(
                        CONFIG_FILE,
                        'r').read().decode('unicode-escape'))
            except IOError:
                pass  # file not existant
        if not self._path or not self._path.exists():
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please choose your projectDirectory.")
            msgBox.exec_()
            self._changeRootDir()
        self.treeView.setPath(self._path)
        abspath = os.path.abspath(self._path)
        self.rootDir.setText(abspath)
        rootLayout.addWidget(self.rootDir)
        # GO UPWARDS ROOT-PATH BUTTON
        btnUpRootDir = QtWidgets.QPushButton('up')
        btnUpRootDir.clicked.connect(self._goUpRootDir)
        rootLayout.addWidget(btnUpRootDir)
        # DEFINE CURRENT DIR AS ROOT-PATH
        btnDefineRootDir = QtWidgets.QPushButton('set')
        btnDefineRootDir.clicked.connect(self._defineRootDir)
        rootLayout.addWidget(btnDefineRootDir)
        # SELECT ROOT-PATH BUTTON
        buttonRootDir = QtWidgets.QPushButton('select')
        buttonRootDir.clicked.connect(self._changeRootDir)
        rootLayout.addWidget(buttonRootDir)
        # NEW-BUTTON
        if self._start_script:
            newButton = QtWidgets.QPushButton('NEW')
            newButton.clicked.connect(self._openNew)
            layout.addWidget(newButton)

    @staticmethod
    def rootDir():
        try:
            return PathStr(
                open(CONFIG_FILE, 'r').read().decode('unicode-escape'))
        except IOError:  # create starter
            return PathStr.home()

    def _goUpRootDir(self):
        self._setRootDir(self._path.dirname())

    def _defineRootDir(self):
        i = self.treeView.selectedIndexes()
        # if not self.treeView.isIndexHidden(i):
        if i:
            if self.fileSystemModel.isDir(i[0]):
                self._setRootDir(PathStr(self.fileSystemModel.filePath(i[0])))

    def _changeRootDir(self):
        path = self.dialogs.getExistingDirectory()
        if path:
            self._setRootDir(path)

    def _setRootDir(self, path):
        self._path = path
        self.rootDir.setText(self._path)
        root = self.fileSystemModel.setRootPath(self._path)
        self.treeView.setRootIndex(root)
        # save last path to file
        if CONFIG_FILE:
            open(CONFIG_FILE, 'w').write(self._path.encode('unicode-escape'))

    def _openNew(self):
        p = spawn.find_executable("python")
        os.spawnl(os.P_NOWAIT, p, 'python', '%s' % self._start_script)


class _FileEditMenu(QtWidgets.QWidget):

    def __init__(self, treeView):
        QtWidgets.QWidget.__init__(self)
        self._treeView = treeView
        self._menu = QtWidgets.QMenu(self)
        d = PathStr.getcwd()
        iconpath = os.path.join(d, 'media', 'icons', 'approve.svg')
        self._actionStart = QtWidgets.QAction(QtGui.QIcon(iconpath),
                                              'Start', self._treeView,
                                              triggered=self._treeView.openProject)

        iconpath = os.path.join(d, 'media', 'icons', 'delete.svg')
        delete = QtWidgets.QAction(QtGui.QIcon(iconpath),
                                   'Delete', self._treeView,
                                   triggered=self._treeView.deleteSelected)

        iconpath = os.path.join(d, 'media', 'icons', 'rename.svg')
        rename = QtWidgets.QAction(QtGui.QIcon(iconpath),
                                   'Rename', self._treeView,
                                   triggered=self._treeView.editSelected)

        iconpath = os.path.join(d, 'media', 'icons', 'new.svg')
        newDir = QtWidgets.QAction(QtGui.QIcon(iconpath),
                                   'New Directory', self._treeView,
                                   triggered=self._treeView.newDirInSelected)

        iconpath = os.path.join(d, 'media', 'icons', 'findReplace.svg')
        self._editStartScript = QtWidgets.QAction(QtGui.QIcon(iconpath),
                                                  'Edit start script', self._treeView,
                                                  triggered=self._treeView.editStartScriptInSelected)

        iconpath = os.path.join(d, 'media', 'icons', 'bug.png')
        self._actionInDebugMode = QtWidgets.QAction(QtGui.QIcon(iconpath),
                                                    'Run in debug mode', self._treeView,
                                                    triggered=self._treeView.runInDebugMode)

        self._menu.addAction(self._actionStart)
        self._menu.addAction(rename)
        self._menu.addAction(newDir)
        self._menu.addAction(self._editStartScript)
        self._menu.addAction(delete)
        self._menu.addAction(self._actionInDebugMode)

    # TODO: does not match signature
    def show(self, evt):
        isDir = self._treeView.selectedIsDir(evt.pos())
        self._actionStart.setVisible(not isDir)
        self._editStartScript.setVisible(not isDir)
        self._actionInDebugMode.setVisible(not isDir)
        self._menu.popup(evt.globalPos())


class _TreeView(QtWidgets.QTreeView):

    def __init__(self):
        super(_TreeView, self).__init__()
        self.setHeaderHidden(False)
        # connect own function for doubleclick
        self.setExpandsOnDoubleClick(False)
        self._menu = _FileEditMenu(self)
        # no editing of the items when clicked, rightclicked, doubleclicked:
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)  # sort by name
        self.setSortingEnabled(True)
        self.setAnimated(True)  # expanding/collapsing animated
        self.setIconSize(QtCore.QSize(60, 60))

        # DRAG/DROP
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.doubleClicked.connect(self._doubleClicked)

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Delete):
            self.deleteSelected()

    def selectionChanged(self, selected, deselected):
        for index in deselected.indexes():
            # print index
            self.closePersistentEditor(index)
        super(_TreeView, self).selectionChanged(selected, deselected)

    def mousePressEvent(self, event):
        mouseBtn = event.button()
        if mouseBtn == QtCore.Qt.RightButton:
            self._menu.show(event)
        super(_TreeView, self).mousePressEvent(event)

    def deleteSelected(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("Are you sure?")
        msgBox.addButton('Yes', QtWidgets.QMessageBox.YesRole)
        msgBox.addButton('No', QtWidgets.QMessageBox.RejectRole)
        ret = msgBox.exec_()
        if ret == 0:  # yes
            self.fileSystemModel.remove(self.currentIndex())

    def selectedIsDir(self, pos):
        index = self.indexAt(pos)
        return self.fileSystemModel.isDir(index)

    def editSelected(self):
        self.openPersistentEditor(self.currentIndex())

    def newDirInSelected(self):
        index = self.currentIndex()
        if not self.fileSystemModel.isDir(index):
            index = index.parent()
        else:
            self.setExpanded(index, True)
        self.fileSystemModel.mkdir(index, 'NEW')

    def editStartScriptInSelected(self):
        index = self.currentIndex()
        self.fileSystemModel.editStartScript(index)

    def dropEvent(self, e):
        index = self.indexAt(e.pos())
        # only insert into directories
        if self.fileSystemModel.isDir(index):
            super(_TreeView, self).dropEvent(e)

    def setModel(self, model):
        self.fileSystemModel = model
        super(_TreeView, self).setModel(model)
        self.setColumnWidth(0, 300)
        self.hideColumn(1)  # type
        self.hideColumn(2)  # size

    def setPath(self, path):
        self._path = path
        root = self.fileSystemModel.setRootPath(self._path)
        self.setRootIndex(root)

    def _doubleClicked(self, index):
        # if folder->toggle expanding
        if self.fileSystemModel.isDir(index):
            self.setExpanded(index, not self.isExpanded(index))
        else:
            self.openProject(index)

    def runInDebugMode(self):
        index = self.currentIndex()
        #term = os.environ.get('TERM')
        self.fileSystemModel.updateStartStript(index)

        if os.name == 'posix':  # linux
            term = 'xterm'
        else:
            sys.exit('debug mode not supported on windows yet')
        subprocess.call([term, '-e',
                         'python %s -d' % self.fileSystemModel.filePath(index)])

    def openProject(self, index=None):
        if not index:
            index = self.currentIndex()
        self.fileSystemModel.updateStartStript(index)
        p = distutils.spawn.find_executable("python")
        # start an indepentent python-process
        os.spawnl(
            os.P_NOWAIT, p, 'python', '%s' %
            self.fileSystemModel.filePath(index))


class _PyzInfo(QtWidgets.QWidget):

    def __init__(self, vsplitter, filesystemmodel, treeView):
        QtWidgets.QWidget.__init__(self)
        self.layout = QtWidgets.QVBoxLayout()
        self._filesystemmodel = filesystemmodel
        self._treeView = treeView

        self.vsplitter = vsplitter
        self.hsplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation(0))
        self.vsplitter.splitterMoved.connect(self.scaleImgV)
        self.hsplitter.splitterMoved.connect(self.scaleImgH)
        self.layout.addWidget(self.hsplitter)
        self._sizeDefined = False
        self.setLayout(self.layout)
        self.img = QtWidgets.QLabel()
        self.text = QtWidgets.QTextEdit()
        self.text.setReadOnly(True)
        self.hsplitter.addWidget(self.img)
        self.hsplitter.addWidget(self.text)

        btnStart = QtWidgets.QPushButton('start')
        self._btnDebug = QtWidgets.QCheckBox('debug mode')

        #labelOpen = QtWidgets.QLabel('open/edit')
        openBox = QtWidgets.QGroupBox('open/edit')
        openBox.setAlignment(QtCore.Qt.AlignHCenter)
        btnCode = QtWidgets.QPushButton('startscript')
        btnActivities = QtWidgets.QPushButton('activities')
        btnLogs = QtWidgets.QPushButton('logs')

        btnStart.clicked.connect(self._startPYZ)
        btnCode.clicked.connect(self._treeView.editStartScriptInSelected)

        lBtn = QtWidgets.QHBoxLayout()
        lStart = QtWidgets.QVBoxLayout()
        lOpen = QtWidgets.QHBoxLayout()
        # lOpen.addWidget(openBox)
        openBox.setLayout(lOpen)
        lBtn.addLayout(lStart)
        lBtn.addWidget(openBox)

        lStart.addWidget(btnStart)
        lStart.addWidget(self._btnDebug)

        #lOpen.addWidget(labelOpen, alignment=QtCore.Qt.AlignCenter)
    #    lOpenBtn = QtWidgets.QHBoxLayout()
        # lOpen.addLayout(lOpenBtn)
        lOpen.addWidget(btnCode)
        lOpen.addWidget(btnActivities)
        lOpen.addWidget(btnLogs)

        self.layout.addLayout(lBtn)

        self.hide()

    def _startPYZ(self):
        if self._btnDebug.isChecked():
            self._treeView.runInDebugMode()
        else:
            self._treeView.openProject()

    def scaleImgV(self, sizeTreeView, pos):
        width = self.vsplitter.sizes()[1] - 30
        self.img.setPixmap(QtGui.QPixmap(self.imgpath).scaledToWidth(width))

    def scaleImgH(self, sizeTreeView, pos):
        height = self.hsplitter.sizes()[0] - 30
        self.img.setPixmap(QtGui.QPixmap(self.imgpath).scaledToHeight(height))

    def update(self, index):
        if self._filesystemmodel.isPyz(index):
            (self.imgpath, description_path) = self._filesystemmodel.extractFiles(
                index, 'screenshot.png', 'description.html')
            # if not self.imgpath:
            #    self.imgpath = self.filesystemmodel.extractFiles(index,'icon')[0]
            #    print self.imgpath
            if self.imgpath:
                if not self._sizeDefined:
                    self._sizeDefined = True
                    width = 400
                    # self.splitter.sizes()[0]*0.5,1)
                    self.vsplitter.moveSplitter(400, 1)
                    self.img.setPixmap(
                        QtGui.QPixmap(
                            self.imgpath).scaledToWidth(width))
                self.img.show()
            else:
                self.img.hide()
            if description_path:
                self.text.setText(file(description_path).read())
            else:
                self.text.setText('<b>No Description found</b>')
            self.show()
        else:
            self.hide()


class _FileSystemModel(QtWidgets.QFileSystemModel):

    def __init__(self, view, file_type):
        QtWidgets.QFileSystemModel.__init__(self, view)
        self.view = view
        self.file_type = file_type

        self.setReadOnly(False)
        self._editedSessions = {}
        self._tmp_dir_work = tempfile.mkdtemp('PYZ-launcher')

    def isPyz(self, index):
        return str(self.fileName(index)).endswith('.%s' % self.file_type)

    def extractFiles(self, index, *fnames):
        extnames = []
        with ZipFile(str(self.filePath(index)), 'r') as myzip:
            for name in fnames:
                try:
                    myzip.extract(name, self._tmp_dir_work)
                    extnames.append(os.path.join(self._tmp_dir_work, name))
                except KeyError:
                    extnames.append(None)
        return extnames

    # TODO: does not match signature
    def data(self, index, role):
        """use zipped icon.png as icon"""
        if index.column() == 0 and role == QtCore.Qt.DecorationRole:
            if self.isPyz(index):
                with ZipFile(str(self.filePath(index)), 'r') as myzip:
                    #    print myzip.namelist()
                    try:
                        myzip.extract('icon', self._tmp_dir_work)
                        p = os.path.join(self._tmp_dir_work, 'icon')
                        return QtGui.QIcon(p)
                    except KeyError:
                        pass
        return super(_FileSystemModel, self).data(index, role)

    def editStartScript(self, index):
        """open, edit, replace __main__.py"""
        f = str(self.fileName(index))
        if f.endswith('.%s' % self.file_type):
            zipname = str(self.filePath(index))
            with ZipFile(zipname, 'a') as myzip:
                # extract+save script in tmp-dir:
                myzip.extract('__main__.py', self._tmp_dir_work)
                tempfilename = f[:-4]
                tempfilepath = os.path.join(self._tmp_dir_work, tempfilename)
                os.rename(
                    os.path.join(
                        self._tmp_dir_work,
                        '__main__.py'),
                    tempfilepath)
                self.openTxt(tempfilepath)
                self._editedSessions[index] = (
                    zipname, self._tmp_dir_work, tempfilename)

    def openTxt(self, path):
        # open and editor (depending on platform):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', path))
        elif os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', path))

    def updateStartStript(self, index):
        if index in self._editedSessions:
            zipname, dirname, tempfilename = self._editedSessions[index]
            tempfilepath = os.path.join(dirname, tempfilename)
            # print dirname, tempfilename
            if os.path.exists(tempfilepath):
                print("adopt changed startScript '%s'" % tempfilename)
                with ZipFile(zipname, 'a') as myzip:
                    myzip.write(tempfilepath, '__main__.py')
                os.remove(tempfilepath)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    a = Launcher()
    a.show()
    sys.exit(app.exec_())

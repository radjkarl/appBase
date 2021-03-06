# -*- coding: utf-8 -*-
from qtpy import QtWidgets
import sys

from appbase.Session import Session


class Application(QtWidgets.QApplication):
    """
    A normal QtWidgets.QApplication
    with embedded session management
    """

    def __init__(self, args, **kwargs):

        QtWidgets.QApplication.__init__(self, args)
        # add session features (load, save, restore state etc) can be found in:
        self.session = Session(args, **kwargs)
        # tell the session when to run the quit procedure:
        self.lastWindowClosed.connect(self.session.quit)

        if sys.platform.startswith("win"):
            # Don't display the Windows GPF dialog if the invoked program dies.
            # See comp.os.ms-windows.programmer.win32
            # How to suppress crash notification dialog?, Jan 14,2004 -
            # Raymond Chen's response [1]
            import ctypes
            SEM_NOGPFAULTERRORBOX = 0x0002  # From MSDN
            ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)


if __name__ == '__main__':
    app = Application([])
    win = QtWidgets.QMainWindow()
    win.show()
    sys.exit(app.exec_())

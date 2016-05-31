=============================================
AppBase - your base for PyQt4 app development
=============================================

.. image:: https://img.shields.io/badge/License-GPLv3-red.svg
.. image:: https://img.shields.io/badge/python-2.6%7C2.7-yellow.svg

- Browse the `API Documentation <http://radjkarl.github.io/appBase>`_
- Fork the code on `github <https://github.com/radjkarl/appBase>`_


.. image:: https://raw.githubusercontent.com/radjkarl/appBase/master/appbase_showcase.png
    :align: center
    :alt: showcase


It includes:

* **Application.py** - just substitute your QApplication this one and you get...
   
   * open, save, new, timed autosave etc.
      
* **MainWindow.py** - this mainWindow gives you a predefined menubar including all features of Application.py
* **MultiWorkspaceWindow.py** - mainWindow with workspace management
* **Server.py** - a system tray control for the mainWindow

DEPRECIATED:
* **Launcher.py** - a graphical launcher to view and open python sessions stored as .pyz


Installation
^^^^^^^^^^^^

**appBase** is listed in the Python Package Index. You can install it typing::

    pip install appBase


Session management
^^^^^^^^^^^^^^^^^^
* Load and save your session as a zipped file
* Save and restore temporal states of your session (Menubar->State)
* Handle multiple workspaces in one window  (Menubar->Workspace)


Tests
^^^^^
To open an example window type::

    python -m appBase.MultiWorkspaceWindow


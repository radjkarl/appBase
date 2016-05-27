=======================================
AppBase - your base for app development
=======================================

Appbase is a foundation for pyQt based applications.

- Browse the `API Documentation <http://radjkarl.github.io/appBase>`_
- Fork the code on `github <https://github.com/radjkarl/appBase>`_


.. image:: https://github.com/radjkarl/appBase/blob/master/appbase_showcase.png
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


Session management
^^^^^^^^^^^^^^^^^^
* Load and save your session as a zipped file
* Save and restore temporal states of your session (Menubar->State)
* Handle multiple workspaces in one window  (Menubar->Workspace)


Tests
^^^^^
To open an example window type::

    python -m appBase.MultiWorkspaceWindow


=======================================
AppBase - your base for app development
=======================================

Appbase is the foundation for a pyQt based application

- Browse the `API Documentation <http://radjkarl.github.io/appBase>`_
- Fork the code on `github <https://github.com/radjkarl/appBase>`_

It includes:

	* **Launcher.py** - a graphical launcher to view and open python sessions stored as *.pyz
	* **Application.py** - just substitude yout QApplication this one and you get...
   
		* open, save, new, timed autosave etc.
      
	* **MainWindow.py** - this mainWindow gives you a predefined menubar including all features of application.py
   * **MultiWorkspaceWindow.py** - mainWindow with workspace management
   * **Server.py** - a system tray control for the mainWindow


During the install procedure you also have the option to add a launcher in your start menu launching the Launcher.py under default conditions.

The Launcher itsef is highly customable alowing different headers, logos and file types to start.
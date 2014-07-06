========================================
AppBase - your base for app development
========================================

AppBase uses the feature of QtRec (ADD LINK) to log every change in 
a graphical environment and to create a simple python scipt to restore a saved state
to give you a solid base for session management

This includes:
	* **launcher.py** - a graphical launcher to view and open python sessions stored as *.pyz
	* **application.py** - just substitude yout QApplication this one and you get...
		* open, save, new, timed autosave etc.
	* **mainwindow.py** - this mainWindow gives you a predefined menubar including all features of application.py


During the install procedure you also have the option to add a launcher in your start menu launching the Launcher.py under default conditions.

The Launcher itsef is highly customable alowing different headers, logos and file types to start.

	
See **examples.py** for more information!



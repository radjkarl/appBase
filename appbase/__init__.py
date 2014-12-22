# -*- coding: utf-8 -*-
'''
Appbase is the foundation for a pyQt based application including:

* save, load, autosave
* fullscreen with F11
* close-dialog
* system tray control
'''


import os as _os
# try:
# 	from Application import Application
# 	from Launcher import Launcher
# 	from MainWindow import MainWindow
# 	from Server import Server
# 	from MultiWorkspaceWindow import MultiWorkspaceWindow
# except ImportError, err:
# 	print err # package not jet installed

__version__ = '0.2.0'
__author__ = 'Karl Bedrich'
__email__ = 'karl@bedrich.de'
__url__ = 'http://pypi.python.org/pypi/AppBase/'
__license__ = 'GPLv3'
__description__ = __doc__
__depencies__= [
		"ordereddict >= 1.1",
		"numpy >= 1.7.1",
		#"PyQt4 >= 4.11.3",
		"fancytools >= 0.2",
		"fancywidgets >= 0.1"
	]
__classifiers__ = [
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Other Audience',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Scientific/Engineering :: Information Analysis',
		'Topic :: Scientific/Engineering :: Visualization',
		'Topic :: Software Development :: Libraries :: Python Modules',
		]

_path = _os.path.abspath(_os.path.dirname(__file__))
logo_path = _os.path.join(_path,'media','logo.svg')
icon_path = _os.path.join(_path,'media','icons')
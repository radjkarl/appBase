# -*- coding: utf-8 -*-
import os

__version__ = '0.1.0'
__author__ = 'Karl Bedrich'
__email__ = 'karl@bedrich.de'
__url__ = 'http://pypi.python.org/pypi/AppBase/'
__license__ = 'GPLv3'
__description__ = '...'#TODO
__depencies__= [
		"ordereddict >= 1.1",
		"numpy >= 1.7.1"
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

_path = os.path.abspath(os.path.dirname(__file__))
logo_path = os.path.join(_path,'media','logo.svg')
icon_path = os.path.join(_path,'media','icons')




#import sys, inspect
##insert this appbase module to sysmodules to allow to import this 'appbase' from everywherwe
#cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
#if cmd_folder not in sys.path:
	#sys.path.insert(0, cmd_folder)
#"""
#nIOp - grab, filter, process and plot nDimensional-data
#http://radjkarl.github.io/nIOp/

#* loads identity
#* loads global config
#* provides QTGui
#"""

#load all modules:
#__all__ = ["I will get rewritten"]
## Don't modify the line above, or this line!
#import automodinit
#automodinit.automodinit(__name__, __file__, globals())
#del automodinit
# Anything else you want can go after here, it won't get modified.
#appBase = __package__

#print __name__

#import appBase
##import identity as genericIdentity
##print __name__
##foreign
##from QtRec import QtGui
##import os


##creating multiple QApplication can cause Exceptions, so load it only one time:
##TODO: root_dir auf identitynamen anpassen
##appBase.QApp = QtGui.QApplication([])
#appbase._config_file = PathStr.home().join('.%s' %__name__)

#try:
	#appbase.root_dir = PathStr(open(appbase._config_file, 'r').read().decode('unicode-escape'))
#except IOError:#create starter
	#appbase.root_dir = PathStr.home()


#@root_dir.setter
#def setRootDir():
	#open(appbase._config_file, 'w').write(appbase.root_dir.encode('unicode-escape'))





#@property
#def root_dir():
	#'''the main directory stored in file'''
	##if not _root_dir:
	#try:
		#return open(_config_file, 'r').read().decode('unicode-escape')
	#except IOError:
		##create new config-file
		#f = open(_config_file, 'w')
		#f.close()
		#return '' #new config-file is empty
#
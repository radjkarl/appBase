# -*- coding: utf-8 -*-

from fancytools.os import PathStr

#foreign
from PyQt4 import QtGui
#import appBase

#import os



#def _checkDir(kwargs):
	#'''
	#if no directory is given use appbase.root_dir
	#'''
	#d = kwargs.get('directory')
	#if not d:
		#kwargs['directory'] = appBase.root_dir
	#return kwargs


def getSaveFileName(**kwargs):
	'''
	analoque to QtGui.QFileDialog.getSaveFileNameAndFilter
	but returns the filename + chosen fileending even if not typed in gui
	'''
	#kwargs = _checkDir(kwargs)
	if 'caption' not in kwargs:
		kwargs['caption'] = 'Save File'
	(fname,ffilter) = QtGui.QFileDialog.getSaveFileNameAndFilter(**kwargs)

	fname = unicode(fname)
	ffilter = unicode(ffilter)
	if  '.' not in fname:
		i = ffilter.index('*')+1
		for o,z in enumerate(ffilter[i:]):
			if z in (' ', ')'):
				break
		ffilter = ffilter[i:o+i]
		fname = fname + ffilter
	return PathStr(fname)


def getOpenFileName(**kwargs):
	#kwargs = _checkDir(kwargs)
	if 'caption' not in kwargs:
		kwargs['caption'] = 'Open File'
	fname = QtGui.QFileDialog.getOpenFileName(**kwargs)
	#this [f***ing] bug occurs only on windows
	#if type(fname) == tuple:
	#	fname = fname[0]
	return PathStr(fname)


def getExistingDirectory(**kwargs):
	#kwargs = _checkDir(kwargs)
	if 'caption' not in kwargs:
		kwargs['caption'] = 'Open Folder'
	fname = QtGui.QFileDialog.getExistingDirectory(**kwargs)
	#this [f***ing] bug occurs only on windows
	#if type(fname) == tuple:
	#	fname = fname[0]
	return PathStr(fname)
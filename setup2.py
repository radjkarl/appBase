# -*- coding: utf-8 -*-
from distutils.core import setup, find_packages
import os
import sys
import shutil
import site

import stat

import identity as genericIdentity
from fancy import stitchModules


class Setup(object):
	
	def __init__(self, identity=genericIdentity, createStarter=True):
		self.identity = stitchModules(identity,genericIdentity)
		
		self.mainPath = os.path.abspath(os.path.dirname(__file__))
		#get installpath
		if os.name == 'posix':#linux
			self.instpath = site.getsitepackages()[0]
		else: #windows
			self.instpath = site.getsitepackages()[1]
		
		if not sys.argv or 'install' in sys.argv:
			self.install()
			if createStarter:
				self.createStarter()
		if 'remove' in sys.argv:
			self.remove()


	def install(self):
		#when no arguments are given: execute python setup.py clean --all install
		for c in ['clean','--all', 'install']:
			if c not in sys.argv:
				sys.argv.append(c)
		
		## generate list of all sub-packages
		#n = len(self.mainPath.split(os.path.sep))
		#subdirs = [i[0].split(os.path.sep)[n:] for i in os.walk(self.mainPath) if '__init__.py' in i[2]]
		#all_packages = ['.'.join(p) for p in subdirs]
		
		

		#do the actual install-procedure
		setup(name= self.identity.NAME,
				#TODO: in identity rein
			version = self.identity.VERSION,
			description = self.identity.DESCRIPTION,
			long_description = self.identity.LONG_DESCRIPTION,
			author = self.identity.AUTHOR,
			author_email = self.identity.EMAIL,
			url = self.identity.PROJECT_SITE,
			packages = find_packages(exclude=['tests*']),#all_packages,
			data_files  = [],
			classifiers = self.identity.CLASSIFIERS
			)
		self.cleanInstall()




	def remove(self):
		shutil.rmtree(self.instpath,self.identity.NAME)
		if os.name == 'posix': #for linux-systems
			os.remove('/usr/share/applications/%s.desktop' %self.identity.NAME)


	def cleanInstall(self):
		#copy all media-files in the python-path
		frommediapath = os.path.join(os.path.abspath(os.path.dirname(__file__)),self.identity.NAME,'media')
		tomediaPath = os.path.join(self.instpath,self.identity.NAME,"media")
		if os.path.exists(tomediaPath):
			shutil.rmtree(tomediaPath)
		shutil.copytree(frommediapath,tomediaPath)
			
		#remove the temp-dir
		shutil.rmtree(os.path.join(self.mainPath,'build'))
	

	def createStarter(self):
		#create starter
		if os.name == 'posix': #for linux-systems
			#create menu entry [for this user] (for gnome, kde, xcfe etc.)
			filename = '/usr/share/applications/%s.desktop' %self.identity.NAME
			iconPath = os.path.join(self.instpath, self.identity.LOGO)#'%s/nIOp/media/logo.svg' %path
			#launcherpath = os.path.join(installpath, launcherfile)
			#write into starter file
			with open(filename, 'w') as f:
				text = '''
[Desktop Entry]
Version=%s
Name=%s
Comment=%s
Icon=%s
Exec=python %s
Terminal=false
Type=Application
Categories=Application;Science;Graphics;Office;
MimeType=PYZ''' %(
			self.identity.VERSION,
			self.identity.NAME,
			self.identity.DESCRIPTION, iconPath,self.identity.LAUNCHER_FILE)
				#enable unicode-characters ('ä' etc.) and write to file
				f.write( text.encode('UTF-8') )
			os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)


if __name__ == '__main__':
	Setup(createStarter=False)
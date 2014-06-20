# -*- coding: utf-8 -*-
'''
usage:
 (sudo) python setup.py +
	 install		... local
	 register		... at http://pypi.python.org/pypi
	 sdist			... create *.tar to be uploaded to pyPI
	 sdist upload	... build the package and upload in to pyPI
'''

#########################
import appbase# as package
#########################

import sys
from fancytools.os import setup

setup(appbase)



##########################
if 'install' in sys.argv:
	try:
		import post_install_routine
	except ImportError:
		pass

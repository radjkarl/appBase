# -*- coding: utf-8 -*-
'''
appbase is the foundation for a pyQt based application including:

* save, load, autosave
* session management
* fullscreen with F11
* close-dialog
* system tray control
'''


import os as _os

__version__ = '0.3.1'
__author__ = 'Karl Bedrich'
__email__ = 'karl@bedrich.de'
__url__ = 'https://github.com/radjkarl/appbase'
__license__ = 'GPLv3'
__description__ = __doc__
__depencies__ = [
        "numpy >= 1.7.1",
        # "PyQt4 >= 4.11.3", # not installable through pip
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

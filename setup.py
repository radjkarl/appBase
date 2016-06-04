# -*- coding: utf-8 -*-
'''
usage:
 (sudo) python setup.py +
     install        ... local
     register        ... at http://pypi.python.org/pypi
     sdist            ... create *.tar to be uploaded to pyPI
     sdist upload    ... build the package and upload in to pyPI
'''

import os
import shutil
from setuptools import find_packages
from setuptools import setup as setup
import appbase as package

# a template for the  python setup.py installer routine
#     
# * take setup information from the packages __init__.py file
#     * this way these informations, like...
#         - __email__
#         - __version__
#         - __depencies__
#         are still available after installation
#             
# * exclude /tests*
# * create scripts from all files in /bin
# * create the long description from 
#     - /README.rst
#     - /CHANGES.rst
#     - /AUTHORS.rst
#
# * remove /build at the end


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    p = os.path.join(*paths)
    if os.path.exists(p):
        with open(p, 'r') as f:
            return f.read()
    return ''
    
setup(
    name            = package.__name__,
    version         = package.__version__,
    author            = package.__author__,
    author_email    = package.__email__,
    url                = package.__url__,
    license            = package.__license__,
    install_requires= [
        "numpy >= 1.7.1",
        # "PyQt4 >= 4.11.3", # not installable through pip
        "fancytools >= 0.2",
        "fancywidgets >= 0.1"
    ],
    classifiers        = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    description        = package.__doc__,
    packages        = find_packages(exclude=['tests*']),
    include_package_data=True,
#     scripts            = [] if not os.path.exists('bin') else [
#                         os.path.join('bin',x) for x in os.listdir('bin')],
    long_description=(
        read('README.rst') + '\n\n' +
        read('CHANGES.rst') + '\n\n' +
        read('AUTHORS.rst'))
    )
# remove the build
# else old and notexistent files could come again in the installed pkg
mainPath = os.path.abspath(os.path.dirname(__file__))
bPath = os.path.join(mainPath,'build')
if os.path.exists(bPath):
    shutil.rmtree(bPath)



# if __name__ == '__main__':
#     import appbase
#     import sys
#     
#     setup(appbase)
#     
#     
#     #LAUNCHER NEEDS SOME WORK - UNTIL THATS DONE: DONT RUN THE FOLLOWING
#     INSTALL_LAUNCHER_STARTER = False
#     
#     if INSTALL_LAUNCHER_STARTER:
#         if 'install' in sys.argv:
#             while True:
#                 answer = raw_input('Do you want to a start menu entry for the appbase Launcher? [Y,N] ')
#                 if answer.lower() in ('y', 'n', ''):
#                     break
#                 print("Please answer with 'Y' or 'N'")
#             if answer == 'Y':
#                 from fancytools.os import StartMenuEntry
#                 from appbase.Launcher import Launcher
#                 icon = os.path.join(os.curdir, 'media', 'launcher_logo.svg')
#                 StartMenuEntry('pyz_launcher', Launcher.__file__, os.path.abspath(icon)).create()


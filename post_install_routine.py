# -*- coding: utf-8 -*-
from fancytools.os import StartMenuEntry
from appbase import launcher


StartMenuEntry('pyz_launcher', launcher.__file__, launcher.ICON).create()


#!/usr/bin/env python
#
#       setup.py
#       
#       Copyright 2009 Sven Festersen <sven@sven-festersen.de>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
from distutils.core import setup

setup(name='PictureView',
      version='beta',
      license='GPL',
      description='A simple photo viewing widget.',
      author='Sven Festersen',
      author_email='sven@sven-festersen.de',
      url='http://sven-festersen.de/drupal/PictureView',
      packages=['picture_view'],
      package_dir={"picture_view":"src/picture_view"})


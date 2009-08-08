#!/usr/bin/env python
#
#       A simple PictureView demo
#       Copyright 2009 Sven Festersen
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
"""
This small application demonstrates the basic usage of the PictureView
widget. 
Run
    python simple_viewer.py /path/to/picture
to see it in action.

Author: Sven Festersen (sven@sven-festersen.de)
Homepage: http://sven-festersen.de
License: GPL (see above)
"""

import gtk
import os
import pygtk
import sys

from picture_view.view import PictureView

def make_title(window, view):
    fn = os.path.basename(view.get_filename())
    percent = int(view.get_zoom() * 100)
    window.set_title("%s (%s%%)" % (fn, percent))

def cb_zoom(widget, zoom, window):
    """
    This callback is executed when the 'zoom-changed' signal of the
    PictureView is emitted.
    """
    make_title(window, widget)
    
def cb_filename(widget, fn, window):
    """
    This callback is executed when the 'filename-changed' signal of the
    PictureView is emitted.
    """
    make_title(window, widget)

if __name__ == "__main__":
    w = gtk.Window()
    w.resize(400, 300)
    w.connect("destroy", gtk.main_quit)
    if len(sys.argv) < 2:
        #no path to picture given => show blank view
        pw = PictureView()
    else:
        pw = PictureView(sys.argv[1])
    pw.connect("zoom-changed", cb_zoom, w)
    pw.connect("filename-changed", cb_filename, w)
    pw.set_background_color(gtk.gdk.color_parse("#424242"))
    w.add(pw)
    w.show_all()
    gtk.main()

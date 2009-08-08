#!/usr/bin/env python
#
#       PictureView
#       Copyright (C) 2009 Sven Festersen
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
PictureView is a PyGTK widget that can be used to build an application
that shows pictures, e.g. a photo browser.
Similar to the most dektop environments' picture viewers it has
controls to zoom (zoom in, zoom out, fit to window, original size) the
picture and to switch between pictures in a directory.
An example of a very basic picture viewer is located in the 'demo'
directory.

Author: Sven Festersen (sven@sven-festersen.de)
License: GPL (see above)
"""
import gobject
import gtk
import os
import pygtk


def get_supported_extensions():
    """
    Returns a list of filename extensions supported by gtk.gdk.Pixbuf.
    """
    res = []
    formats = gtk.gdk.pixbuf_get_formats()
    for format in formats:
        res += format["extensions"]
    return res


SUPPORTED_EXTENSIONS = get_supported_extensions()

MODE_FIT_WINDOW = 0
MODE_FIXED_ZOOM = 1


def get_image_files(dir):
    """
    Returns a list of all image files in the directory dir that are
    supported by gtk.gdk.Pixbuf.
    """
    res = []
    for filename in os.listdir(dir):
        fnlow = filename.lower()
        base, ext = os.path.splitext(fnlow)
        if ext.strip(".") in SUPPORTED_EXTENSIONS:
            res.append(filename)
    res.sort()
    return res


class PictureView(gtk.VBox):
    
    __gproperties__ = {"mode": (gobject.TYPE_INT, "view mode",
                                "The mode of the view.",
                                0, 1, 0, gobject.PARAM_READWRITE),
                        "filename": (gobject.TYPE_STRING, "filename",
                                "The picture filename.", "",
                                gobject.PARAM_READWRITE),
                        "show-navigation": (gobject.TYPE_BOOLEAN,
                                            "show navigation",
                                            "Set whether to show prev/next buttons.",
                                            True, gobject.PARAM_READWRITE),
                        "background-color": (gobject.TYPE_PYOBJECT,
                                                "background color",
                                                "The background color.",
                                                gobject.PARAM_READWRITE),
                        "zoom": (gobject.TYPE_FLOAT, "zoom factor",
                                "The zoom factor.", 0.0, 100, 1.0, gobject.PARAM_READWRITE)}
                                
    __gsignals__ = {"zoom-changed": (gobject.SIGNAL_RUN_LAST,
                                        gobject.TYPE_NONE,
                                        (gobject.TYPE_FLOAT,)),
                    "filename-changed": (gobject.SIGNAL_RUN_LAST,
                                        gobject.TYPE_NONE,
                                        (gobject.TYPE_STRING,))}
    
    def __init__(self, filename=""):
        gtk.VBox.__init__(self)
        
        self._zoom = 1.0
        self._show_navigation = True
        self._mode = MODE_FIT_WINDOW
        self._filename = os.path.abspath(filename)
        self._dir = ""
        self._file_list = []
        self._index = 0
        self._pixbuf = None
        self._background_color = gtk.gdk.Color()
            
        self._init_image()
        self._init_controls()
        
        self.set_property("can-focus", True)
        self.connect("key-press-event", self._cb_key_press_event)
        self.connect("filename-changed", self._cb_filename_changed)
        self.connect("size-allocate", self._cb_allocate)
        
        if filename:
            self._pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
            self._init_file_list()
            self.emit("filename-changed", self._filename)
        
    def _init_file_list(self):
        dir = os.path.dirname(self._filename)
        if dir != self._dir:
            files = get_image_files(dir)
            files.sort()
            self._file_list = map(lambda x: os.path.abspath(dir + os.sep + x), files)
            self._index = 0
            for i, fn in enumerate(self._file_list):
                if fn == self._filename:
                    self._index = i
            self._dir = dir
        
    def do_get_property(self, property):
        if property.name == "mode":
            return self._mode
        elif property.name == "filename":
            return self._filename
        elif property.name == "show-navigation":
            return self._show_navigation
        elif property.name == "background-color":
            return self._background_color
        elif property.name == "zoom":
            return self._zoom
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "mode":
            self._mode = value
            self._scale_pixbuf()
        elif property.name == "filename":
            self._filename = os.path.abspath(value)
            self._pixbuf = gtk.gdk.pixbuf_new_from_file(self._filename)
            self._scale_pixbuf()
            self._init_file_list()
            self.emit("filename-changed", self._filename)
        elif property.name == "show-navigation":
            self._show_navigation = value
            if value:
                self._hbox_navigation.show()
                self._separator_navigation.show()
            else:
                self._hbox_navigation.hide()
                self._separator_navigation.hide()
            self._info_changed()
        elif property.name == "background-color":
            self._background_color = value
            self._event_box.modify_bg(gtk.STATE_NORMAL, self._background_color)
        elif property.name == "zoom":
            self._zoom = value
            self._mode = MODE_FIXED_ZOOM
            self._scale_pixbuf()
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def _init_image(self):
        self._scrolled = gtk.ScrolledWindow()
        self._event_box = gtk.EventBox()
        self._image = gtk.Image()
        
        self._scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self._event_box.modify_bg(gtk.STATE_NORMAL, self._background_color)
        
        self._event_box.add(self._image)
        self._scrolled.add_with_viewport(self._event_box)
        self.pack_start(self._scrolled)
        
    def _init_controls(self):
        self._hbox_navigation = gtk.HBox()
        self._hbox_zoom = gtk.HBox()
        hbox = gtk.HBox()
        
        hbox.set_spacing(6)
        hbox.set_border_width(6)
        
        hbox.pack_start(self._hbox_navigation, False, False)
        self._separator_navigation = gtk.VSeparator()
        hbox.pack_start(self._separator_navigation, False, False)
        hbox.pack_start(self._hbox_zoom, False, False)
        
        self._button_previous = gtk.Button()
        self._button_next = gtk.Button()
        
        self._button_previous.connect("clicked", self._cb_button_previous)
        self._button_next.connect("clicked", self._cb_button_next)
        
        self._button_previous.set_image(gtk.image_new_from_stock(gtk.STOCK_GO_BACK, gtk.ICON_SIZE_MENU))
        self._button_next.set_image(gtk.image_new_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_MENU))
        
        self._button_previous.set_relief(gtk.RELIEF_NONE)
        self._button_next.set_relief(gtk.RELIEF_NONE)
        
        self._button_previous.set_focus_on_click(False)
        self._button_next.set_focus_on_click(False)
        
        self._hbox_navigation.pack_start(self._button_previous, False, False)
        self._hbox_navigation.pack_start(self._button_next, False, False)
        
        
        self._button_zoom_out = gtk.Button()
        self._button_zoom_in = gtk.Button()
        self._button_zoom_fit = gtk.Button()
        self._button_zoom_normal = gtk.Button()
        
        self._button_zoom_out.connect("clicked", self._cb_button_zoom_out)
        self._button_zoom_in.connect("clicked", self._cb_button_zoom_in)
        self._button_zoom_fit.connect("clicked", self._cb_button_fit)
        self._button_zoom_normal.connect("clicked", self._cb_button_normal)
        
        self._button_zoom_out.set_image(gtk.image_new_from_stock(gtk.STOCK_ZOOM_OUT, gtk.ICON_SIZE_MENU))
        self._button_zoom_in.set_image(gtk.image_new_from_stock(gtk.STOCK_ZOOM_IN, gtk.ICON_SIZE_MENU))
        self._button_zoom_fit.set_image(gtk.image_new_from_stock(gtk.STOCK_ZOOM_FIT, gtk.ICON_SIZE_MENU))
        self._button_zoom_normal.set_image(gtk.image_new_from_stock(gtk.STOCK_ZOOM_100, gtk.ICON_SIZE_MENU))
        
        self._button_zoom_out.set_relief(gtk.RELIEF_NONE)
        self._button_zoom_in.set_relief(gtk.RELIEF_NONE)
        self._button_zoom_fit.set_relief(gtk.RELIEF_NONE)
        self._button_zoom_normal.set_relief(gtk.RELIEF_NONE)
        
        self._button_zoom_out.set_focus_on_click(False)
        self._button_zoom_in.set_focus_on_click(False)
        self._button_zoom_fit.set_focus_on_click(False)
        self._button_zoom_normal.set_focus_on_click(False)
        
        self._hbox_zoom.pack_start(self._button_zoom_out, False, False)
        self._hbox_zoom.pack_start(self._button_zoom_in, False, False)
        self._hbox_zoom.pack_start(self._button_zoom_fit, False, False)
        self._hbox_zoom.pack_start(self._button_zoom_normal, False, False)
        
        self._label_info = gtk.Label()
        self._label_info.set_alignment(1.0, 0.5)
        hbox.pack_start(self._label_info)
        
        self.pack_start(hbox, False, False)
        
    def _scale_pixbuf(self):
        if self._pixbuf == None: return
        p_width = self._pixbuf.get_width()
        p_height = self._pixbuf.get_height()
        
        if self._mode == MODE_FIT_WINDOW:
            self._scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
            s_x, s_y, s_width, s_height = self._scrolled.get_allocation()
            if p_width > s_width or p_height > s_height:
                a = float(s_width) / p_width
                b = float(s_height) / p_height
                f = min(a, b)
                
                n_width = int(p_width * f)
                n_height = int(p_height * f)
                pb = self._pixbuf.scale_simple(n_width, n_height, gtk.gdk.INTERP_HYPER)
                self._zoom = f
                self.emit("zoom-changed", self._zoom)
            else:
                pb = self._pixbuf
                self._zoom = 1.0
                self.emit("zoom-changed", self._zoom)
        else:
            self._scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            n_width = int(p_width * self._zoom)
            n_height = int(p_height * self._zoom)
            pb = self._pixbuf.scale_simple(n_width, n_height, gtk.gdk.INTERP_HYPER)
        
        self._image.set_from_pixbuf(pb)
        
    def _cb_allocate(self, widget, allocation):
        self._scale_pixbuf()
        
    def _cb_button_fit(self, button):
        self._scrolled.set_size_request(0, 0)
        self.set_property("mode", MODE_FIT_WINDOW)
        
    def _cb_button_normal(self, button):
        self._zoom = 1.0
        self.set_property("mode", MODE_FIXED_ZOOM)
        self.emit("zoom-changed", self._zoom)
        
    def _cb_button_zoom_in(self, button):
        self._zoom += 0.1
        self.set_property("mode", MODE_FIXED_ZOOM)
        self.emit("zoom-changed", self._zoom)
        
    def _cb_button_zoom_out(self, button):
        self._zoom -= 0.1
        self.set_property("mode", MODE_FIXED_ZOOM)
        self.emit("zoom-changed", self._zoom)
        
    def _cb_button_previous(self, button):
        self.previous()
        
    def _cb_button_next(self, button):
        self.next()
        
    def _cb_filename_changed(self, widget, filename):
        self._info_changed()
        
    def _info_changed(self):
        self.grab_focus()
        fn = os.path.basename(self._filename)
        txt = "%s" % fn
        if self._show_navigation:
            txt = "%s (%s/%s)" % (fn, self._index + 1, len(self._file_list))
        self._label_info.set_label(txt)
        
    def _cb_key_press_event(self, widget, event):
        if not self._show_navigation: return
        
        if event.keyval in [65361, 65362]:
            self.previous()
        elif event.keyval in [65363, 65364, 32, 65293]:
            self.next()
        elif event.keyval == 102:
            self._cb_button_fit(widget)
        elif event.keyval == 103:
            self._cb_button_normal(widget)
        elif event.keyval == 43:
            self._cb_button_zoom_in(widget)
        elif event.keyval == 45:
            self._cb_button_zoom_out(widget)
        self.grab_focus()
        
    def next(self):
        """
        Load the next picture that's in the same directory as the
        current picture.
        """
        if self._index < len(self._file_list) - 1:
            fn = self._file_list[self._index + 1]
            self._index += 1
        else:
            fn = self._file_list[0]
            self._index = 0
        self.set_property("filename", fn)
        
    def previous(self):
        """
        Load the previous picture that's in the same directory as the
        current picture.
        """
        if self._index > 0:
            fn = self._file_list[self._index - 1]
            self._index -= 1
        else:
            fn = self._file_list[len(self._file_list) - 1]
            self._index = len(self._file_list) - 1
        self.set_property("filename", fn)
        
    def set_background_color(self, color):
        """
        Set the background color.
        
        @param color: the new background color
        @type color: gtk.gdk.Color.
        """
        self.set_property("background-color", color)
        
    def get_background_color(self):
        """
        Returns the current background color.
        
        @return: gtk.gdk.Color.
        """
        return self.get_property("background-color")
        
    def set_filename(self, filename):
        """
        Use this method to load and display the picture specified by
        filename.
        
        @param filename: the path to the picture to load
        @type filename: string.
        """
        self.set_property("filename", filename)
        
    def get_filename(self):
        """
        Returns the path to the current displayed picture or an empty
        string if no picture is displayed.
        
        @return: string.
        """
        return self.get_property("filename")
        
    def set_mode(self, mode):
        """
        Set the zoom mode of the widget. mode has to be MODE_FIT_WINDOW
        (default) or MODE_FIXED_ZOOM.
        
        @param mode: the zoom mode of the widget
        @type mode: one of the mode constants above.
        """
        self.set_property("mode", mode)
        
    def get_mode(self):
        """
        Returns the current zoom mode.
        
        @return: a mode constant.
        """
        return self.get_property("mode")
        
    def set_show_navigation(self, show):
        """
        Set whether navigation arrows (to switch to next and previous
        pictures in the same directory as the current) should be shown.
        If True, the number of pictures and the current picture's index
        are also shown in the bottom right corner.
        
        @type show: boolean.
        """
        self.set_property("show-navigation", show)
        
    def get_show_navigation(self):
        """
        Returns True if navigation elements are shown (see method
        set_show_navigation for details).
        
        @return: boolean.
        """
        return self.get_property("show-navigation")
        
    def set_zoom(self, zoom):
        """
        Use this method to set the zoom level manually. If set, the
        mode will be changed to MODE_FIXED_ZOOM.
        
        @param zoom: the new zoom level
        @type zoom: float.
        """
        self.set_property("zoom", zoom)
        
    def get_zoom(self):
        """
        Returns the current zoom level.
        
        @return: float.
        """
        return self.get_property("zoom")

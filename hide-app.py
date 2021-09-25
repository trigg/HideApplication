#!/usr/bin/python

# Copyright 2021 Nathan Howard
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import gi
import os
from xdg.DesktopEntry import DesktopEntry
gi.require_version("Gtk", "3.0")
# pylint: disable=wrong-import-position,wrong-import-order
from gi.repository import Gtk


class App:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_size_request(300,600)
        self.window.connect("destroy", Gtk.main_quit)
        self.list = {}
        self.filter_string=""
        self.usrshare = "/usr/share/applications/"
        self.localshare = "/usr/local/share/applications/"
        if os.geteuid()>0 :
            self.localshare = os.path.expanduser("~/.local/share/applications/")

    def main(self):
        self.get_applications()

        self.create_window()

    def get_applications(self):
        # List all system files
        self.add_directory(self.usrshare)
        self.add_directory(self.localshare)

    def add_directory(self, dir):
        for file in os.listdir(dir):
            if file.endswith(".desktop"):
                app = DesktopEntry("%s%s" % (dir , file))
                self.list[file]=app

    def filter_changed(self, entry):
        self.filter_string=entry.get_text()
        self.filter.refilter()

    def filter_func(self, model, iter, data):
        if self.filter_string in model[iter][2]:
            return True
        return False

    def create_window(self):
        box = Gtk.VBox(homogeneous=False)

        store = Gtk.ListStore(bool,str, str)
        self.filter = store.filter_new()
        self.filter.set_visible_func(self.filter_func)
        for app in self.list:
            obj = self.list[app]
            name = obj.getName()
            icon = obj.getIcon()
            hidden = obj.getNoDisplay()
            store.append([hidden,icon, name])

        scrolledwindow = Gtk.ScrolledWindow()
        tree = Gtk.TreeView(model=self.filter)

        column = Gtk.TreeViewColumn("Applications")

        toggle = Gtk.CellRendererToggle()
        title = Gtk.CellRendererText()
        icon = Gtk.CellRendererPixbuf()

        column.pack_start(toggle, True)
        column.pack_start(icon, True)
        column.pack_start(title, True)

        column.add_attribute(toggle, "active", 0)
        column.add_attribute(icon, "icon_name",1)
        column.add_attribute(title, "text", 2)

        tree.append_column(column)

        tree.set_activate_on_single_click(True)
        tree.connect("row-activated", self.on_tree_selection_changed)

        filtertext = Gtk.Entry()
        filtertext.connect("changed", self.filter_changed)

        box.pack_start(filtertext,False, False, 0)
        box.pack_end(scrolledwindow,True,True,0)
        scrolledwindow.add(tree)
        self.window.add(box)
        self.window.show_all()

        Gtk.main()

    def on_tree_selection_changed(self, tree, number, selection):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter is not None:
            print("Selected %s"% (model[treeiter][2]))
            model[treeiter][0]= not model[treeiter][0]
            fname, app = self.get_app_named(model[treeiter][2])
            fullfname = os.path.expanduser("%s%s"%(self.localshare, fname))
            if app:
                print("Writing to : %s" % ( fullfname ))
                if model[treeiter][0]:
                    app.set("NoDisplay", 'true')
                else:
                    app.removeKey("NoDisplay")
                app.write(fullfname)

    def get_app_named(self, name):
        for fname in self.list:
            app = self.list[fname]
            if app.getName() == name:
                return [fname, app]
        return [None, None]

if __name__ == '__main__' :
    app = App()
    app.main()

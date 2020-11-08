#! bin/python3
import gi
import time, threading
import sys

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

i = 0
p = 1

class Handler:

    def __init__(self):
      self.isRunning = False

    def onDestroy(self, *args):
        Gtk.main_quit()

    def onDestroy(self, *args):
      Gtk.main_quit()
      sys.exit()

    def on_run(self, button):
      print(self.isRunning)
      file.set_fraction(file.get_fraction() + 0.1)
      self.isRunning = not self.isRunning
      self.givePulse()

    def givePulse(self):
      file.pulse()
      if(self.isRunning):
        threading.Timer(0.5, self.givePulse).start()

builder = Gtk.Builder()
builder.add_from_file("indev.glade")
builder.connect_signals(Handler())

file = builder.get_object("prog")

win = builder.get_object("win")

win.show_all()

# win.connect_handler("destroy", Gtk.main_quit)


Gtk.main()

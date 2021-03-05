import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class Theme:
    
    def __init__(self):
        self.settings = Gtk.Settings.get_default()
    
    def set_dark_theme(self):
        self.settings.set_property("gtk-application-prefer-dark-theme", True)
        
    def set_light_theme(self):
        self.settings.set_property("gtk-application-prefer-dark-theme", False)
     
    def set_system_default(self):
        self.set_light_theme()

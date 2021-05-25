#   ffripper - Audio-CD ripper.
#   Copyright 2020-2021 Stefan Garlonta
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 3 of the License.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#   USA
#

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

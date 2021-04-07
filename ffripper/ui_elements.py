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

gi.require_version('Notify', '0.7')
from gi.repository import Notify


class GladeWindow(object):
    callbacks = {}
    builder = None

    def __init__(self, builder):
        """ Init GladeWindow, stores the objects's potential callbacks for later.
        You have to call connect_signals() when all descendants are ready. """
        GladeWindow.builder = builder
        GladeWindow.callbacks.update(dict([[x, getattr(self, x)]
                                           for x in dir(self) if x.startswith('on_')]))

    def __getattr__(self, attribute):
        """ Allow direct use of window widget. """
        widget = GladeWindow.builder.get_object(attribute)
        if widget is None:
            raise AttributeError('Widget \'%s\' not found' % attribute)
        self.__dict__[attribute] = widget  # cache result
        return widget

    @staticmethod
    def connect_signals():
        """ Connect all GladeWindow objects to theirs respective signals """
        GladeWindow.builder.connect_signals(GladeWindow.callbacks)


class UiObjects:

    @staticmethod
    def chooser():
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)
        folder = None
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
        dialog.destroy()
        return folder


class Dialog:

    def __init__(self, heading, text):
        self.heading = heading
        self.text = text

    def error_dialog(self):
        dialog = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.OK,
                                   text=self.heading,
                                   )
        dialog.format_secondary_text(
            self.text)
        dialog.run()
        dialog.destroy()

    @staticmethod
    def finished_dialog():
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Finished Ripping",
        )
        dialog.format_secondary_text(
            ""
        )
        dialog.run()
        dialog.destroy()

    @staticmethod
    def notify():
        Notify.init("ffripper-1.0")
        notification = Notify.Notification.new(
            "Finished Ripping",
            ""
        )
        notification.show()

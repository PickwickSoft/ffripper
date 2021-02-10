#!/usr/bin/python3
"""
This file creates the ui and runs ffripper
"""
#   ffripper-1.0 - Audio-CD ripper.
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

import os
import gi
import yaml
from threading import Thread
from ffripper.process_launcher import CopyProcessor, CopyProcessorListener
from ffripper.errors import RipperError
from ffripper.metadata import Metadata
from ffripper.cdrom_info_object import CDInfo
from ffripper.track_info import TrackInfo
from ffripper.player import Player
from ffripper.ui_elements import UiObjects, Dialog, ImageContextMenu, GladeWindow
from ffripper.image import Image

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gst, GdkPixbuf, Gdk

formats = ["mp2", "mp3",
           "wav", "ogg",
           "aac", 'opus',
           'flac', 'm4a',
           'wma', 'eac3',
           'au', 'asf',
           'spx', 'voc',
           'aiff', 'caf',
           'ac3', 'oga',
           'afc', 'ast',
           'mp4', 'wmv',
           'avi', 'flv',
           'm4v', 'mka',
           'mkv', 'mov',
           'mpg', 'vob',
           'webm']
formats.sort()
entry = 0
local_mount_point = "/run/user/1000/gvfs/cdda:host=sr0"
music_detect = True
is_running = False
directory_name, filename = os.path.split(os.path.abspath(__file__))
os.chdir(directory_name)


class Loader:

    @staticmethod
    def load_formats(audio_formats):
        for i in range(len(audio_formats) - 1):
            window.format_chooser.append_text(audio_formats[i])
            window.standard_format.append_text(audio_formats[i])

    @staticmethod
    def load_settings():
        with open("../data/settings.yaml") as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)
        autodetect = settings["autodetect"]
        always_eject = settings['always_eject']
        output_folder = settings['outputFolder']
        format_standard = settings['standardFormat']
        if output_folder != '':
            window.output_entry.set_text(output_folder)
        if format_standard is not None:
            for i in range(len(formats) - 1):
                if format_standard == formats[i]:
                    window.format_chooser.set_active(i)


class Preparer:

    def __init__(self, ):
        self.input_dev = local_mount_point
        self.format = window.format_chooser.get_active_text()
        self.output_folder = window.output_entry.get_text()

    def return_all(self):
        return [self.input_dev, self.output_folder, self.format]


class MyCopyListener(CopyProcessorListener):
    @staticmethod
    def on_copy_item(count):
        percentage = 1 / count
        window.progressbar.set_fraction(window.progressbar.get_fraction() + percentage)

    @staticmethod
    def on_filename(file):
        pass


class RipperWindow(GladeWindow):

    def __init__(self, builder):
        GladeWindow.__init__(self, builder)

        self.list_store = Gtk.ListStore(bool, str, str, str)
        self.tracks_2_copy = []
        self.copy_metadata = None
        self.copy = None
        self.metadata = None
        self.thread = Thread(target=self.execute_copy, args=())
        self.cover_art = False
        self.disc_tracks = None
        self.create_treeview()
        self.set_treeview_content()

        self.widget = builder.get_object('main_window')
        self.player = Player(self.refresh_button)
        if os.path.isdir(local_mount_point):
            self.player.set_file(local_mount_point + "/" + self.disc_tracks[0])
        self.slider_handler_id = self.slider.connect("value-changed", self.on_slider_seek)
        GladeWindow.connect_signals()
        self.widget.connect("destroy", Gtk.main_quit)
        self.widget.show_all()

    def create_treeview(self):
        # Toggle Buttons
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)
        column_toggle = Gtk.TreeViewColumn("Import", renderer_toggle, active=0)
        self.tree_view.append_column(column_toggle)

        # Track Numbers
        renderer_track_number = Gtk.CellRendererText()
        column_track_number = Gtk.TreeViewColumn("Nr.", renderer_track_number, text=1)
        self.tree_view.append_column(column_track_number)
        renderer_track_number.connect("edited", self.text_edited)

        # Audio Titles
        renderer_title = Gtk.CellRendererText()
        renderer_title.set_property("editable", True)
        column_title = Gtk.TreeViewColumn("Title", renderer_title, text=2)
        self.tree_view.append_column(column_title)
        renderer_title.connect("edited", self.title_text_edited)

        # Audio Artists
        renderer_artist = Gtk.CellRendererText()
        renderer_artist.set_property("editable", True)
        column_artist = Gtk.TreeViewColumn("Artist", renderer_artist, text=3)
        self.tree_view.append_column(column_artist)
        renderer_artist.connect("edited", self.artist_text_edited)

    def set_treeview_content(self):
        try:
            self.metadata = Metadata()
        except RipperError as error:
            Dialog(error.reason, error.text).error_dialog()
        self.cover_image.connect_object("event", self.image_menu, ImageContextMenu())
        if (self.metadata.get_cover() != "") and (self.metadata.get_cover() is not None):
            self.cover_art = True
            self.cover_image.set_from_pixbuf(Image.bytes2pixbuf(self.metadata.get_cover()))

        # Tracks default
        tracks = None
        try:
            self.disc_tracks = os.listdir(local_mount_point)
        except FileNotFoundError:
            Dialog("No Disc Found", "Please insert a disc and reload Metadata").error_dialog()
            return

        # Write to Entries
        if self.metadata is not None:
            self.artist_entry.set_text(self.metadata.get_artist())
            self.album_entry.set_text(self.metadata.get_album())

            # Metadata append
            tracks = self.metadata.get_tracks()
        try:
            for i in range(len(tracks)):
                self.list_store.append([False, str(i + 1), tracks[i].get_name(), tracks[i].get_artist()])
        except TypeError:
            for j in range(len(self.disc_tracks)):
                self.list_store.append([False, str(j + 1), self.disc_tracks[j], ""])

        self.tree_view.set_model(self.list_store)


    def text_edited(self, widget, path, text):
        self.list_store[path][1] = text

    def on_cell_toggled(self, widget, path):
        self.list_store[path][0] = not self.list_store[path][0]

    def title_text_edited(self, widget, path, text):
        self.list_store[path][2] = text

    def artist_text_edited(self, widget, path, text):
        self.list_store[path][3] = text

    def return_info(self, tracks):
        return CDInfo(self.album_entry.get_text(), self.artist_entry.get_text(), tracks, None)

    def execute_copy(self):
        global is_running
        print("CopyStart")
        info = Preparer().return_all()
        print(info)
        listener = MyCopyListener()
        cover = None
        if self.cover_art:
            cover = Image.bytes2png(self.metadata.get_cover(), info[1], "cover")
        try:
            self.copy = CopyProcessor(info[0], info[1], info[2], listener, self.copy_metadata, self.tracks_2_copy,
                                      cover)
            self.copy.run()
        except RipperError as error:
            print("An Error has occurred: ", error.reason.to_string())
            GLib.idle_add(Dialog(error.reason.to_string(), error.text).error_dialog)
        self.thread = Thread(target=self.execute_copy, args=())
        if window.eject_standard.get_active() == 1:
            os.system("eject")
        GLib.idle_add(self.update_ui, "Rip", 0, "")
        is_running = False

    @staticmethod
    def update_ui(copy_button_title, fraction, filename_label_text):
        # Dialog.finished_dialog()
        Dialog.notify()
        window.copy_button.set_label(copy_button_title)
        window.progressbar.set_fraction(fraction)

    def rip(self):
        if self.is_disc() and window.format_chooser.get_active_text() != "":
            path = window.output_entry.get_text()
            if os.path.isdir(path):
                self.thread.start()
                window.copy_button.set_label("Cancel")
                return
            else:
                window.directory_error.format_secondary_text(path + "\n")
                window.directory_error.run()


    def kill_process(self):
        self.copy.stop_copy()
        self.thread.join()
        window.copy_button.set_label("Rip")
        window.progressbar.set_fraction(0)
        self.thread = Thread(target=self.execute_copy, args=())

    @staticmethod
    def image_menu(widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # make widget popup
            widget.popup(None, None, None, event.button, event.time)

    def on_ok_button_clicked(self, button):
        self.directory_error.hide()

    def on_copy_button_clicked(self, button):
        global is_running
        if self.is_disc() and self.format_chooser.get_active_text() != "":
            if os.path.isdir(window.output_entry.get_text()):
                if not is_running:
                    is_running = True
                    title_numbers = os.listdir(local_mount_point)
                    tracks = []
                    for i in range(len(self.list_store)):
                        if self.list_store[i][0]:
                            self.tracks_2_copy.append(title_numbers[i])
                            tracks.append(TrackInfo(self.list_store[i][2], None, None, self.list_store[i][3]))
                    self.copy_metadata = self.return_info(tracks)
                    self.rip()
                else:
                    self.kill_process()
                    is_running = False

            else:
                self.directory_error.format_secondary_text(window.output_entry.get_text() + "\n")
                self.directory_error.run()

    def on_search_button3_clicked(self, button):
        ui_objects = UiObjects()
        folder = ui_objects.chooser()
        if folder is not None:
            self.standard_output_entry.set_text(folder)

    def on_search_button2_clicked(self, button):
        ui_objects = UiObjects()
        folder = ui_objects.chooser()
        if folder is not None:
            self.output_entry.set_text(folder)

    def on_player_button_clicked(self, button):
        if self.player_button.get_image() == self.play_image:
            self.player_button.set_image(self.pause_image)
            self.player.play()
            GLib.timeout_add(1000, self.update_slider)
        else:
            self.player_button.set_image(self.play_image)
            self.player.pause()

    def update_slider(self):
        if not self.player.is_playing:
            return False
        self.slider.set_range(0, self.player.get_duration())
        self.slider.handler_block(self.slider_handler_id)
        self.slider.set_value(self.player.get_position())
        self.slider.handler_unblock(self.slider_handler_id)

        return True

    def on_slider_seek(self, argument):
        seek_time_secs = self.slider.get_value()
        self.player._player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                        seek_time_secs * Gst.SECOND)

    def on_volume_changed(self, button, volume):
        self.player.set_volume(volume)

    def refresh_button(self, player):
        self.player_button.set_image(self.play_image)

    def on_tree_view_columns_changed(self, widget, row, column):
        print("Changed row: ", row)
        self.player.reset()
        index = int(row.get_indices()[0])
        self.player.set_file(local_mount_point + "/" + self.disc_tracks[index])
        self.player_button.set_image(self.pause_image)
        self.player.play()

    def on_setting_button_clicked(self, button):
        self.settings_window.show_all()
        with open("../data/settings.yaml") as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)
            if settings['always_eject']:
                self.eject_standard.set_active(True)
            if settings['autodetect']:
                self.auto_detect.set_active(True)
            if settings['outputFolder'] != '':
                self.standard_output_entry.set_text(str(settings['outputFolder']))
            if settings['standardFormat'] is not None:
                for i in range(len(formats) - 1):
                    if settings['standardFormat'] == formats[i]:
                        self.standard_format.set_active(i)

    def on_cancel_button_clicked(self, button):
        self.settings_window.hide()

    def on_refresh_button_clicked(self, button):
        self.set_treeview_content()

    @staticmethod
    def on_eject_button_clicked(button):
        os.system("eject")

    def on_apply_button_clicked(self, button):
        with open("../data/settings.yaml") as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)

        settings['autodetect'] = self.auto_detect.get_active()

        with open("../data/settings.yaml", "w") as f:
            yaml.dump(settings, f)

        settings['always_eject'] = self.eject_standard.get_active()

        with open("../data/settings.yaml", "w") as f:
            yaml.dump(settings, f)

        settings['outputFolder'] = self.standard_output_entry.get_text()

        with open("../data/settings.yaml", "w") as f:
            yaml.dump(settings, f)

        settings['standardFormat'] = self.standard_format.get_active_text()

        with open("../data/settings.yaml", "w") as f:
            yaml.dump(settings, f)

        self.settings_window.hide()

        Loader.load_settings()

    def on_about_clicked(self, button):
        about = self.about_dialog
        about.set_transient_for(self.widget)
        about.run()

    def on_aboutdialog_response(self, *args):
        self.about_dialog.hide()

    def __getattr__(self, attribute):
        """ Allow direct use of window widget. """
        widget = self.builder.get_object(attribute)
        if widget is None:
            raise AttributeError('Widget \'%s\' not found' % attribute)
        self.__dict__[attribute] = widget  # cache result
        return widget

    @staticmethod
    def is_disc():
        if os.path.isdir(local_mount_point):
            return True
        print("No Device found")
        Dialog("No Disc Found", "Please insert a disc").error_dialog()
        return False



window = None


def main(builder):
    global window
    window = RipperWindow(builder)
    load = Loader()
    load.load_formats(formats)
    load.load_settings()
    Gtk.main()

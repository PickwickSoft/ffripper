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

import os
import gi
import yaml
from threading import Thread
from process_launcher import CopyProcessor, CopyProcessorListener
from errors import RipperError
from metadata import Metadata
from cdrom_info_object import CDInfo
from track_info import TrackInfo
from player import Player
from ui_elements import UiObjects, Dialog

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gst


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
        for i in range(0, len(audio_formats) - 1):
            format_chooser.append_text(audio_formats[i])
            standard_format.append_text(audio_formats[i])

    @staticmethod
    def load_settings():
        with open("settings.yaml") as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)
        autodetect = settings["autodetect"]
        always_eject = settings['always_eject']
        output_folder = settings['outputFolder']
        format_standard = settings['standardFormat']
        if output_folder != '':
            output.set_text(output_folder)
        if format_standard is not None:
            for i in range(0, len(formats) - 1):
                if format_standard == formats[i]:
                    format_chooser.set_active(i)


class Preparer:

    def __init__(self, ):
        self.input_dev = local_mount_point
        self.format = format_chooser.get_active_text()
        self.output_folder = output.get_text()

    def return_all(self):
        prepared_list = [self.input_dev, self.output_folder, self.format]
        return prepared_list


class MetadataTreeview:

    def __init__(self):
        try:
            self.metadata = Metadata()
        except RipperError as error:
            Dialog(error.reason, error.text).error_dialog()
            self.metadata = None
        self.t = Thread(target=self.execute_copy, args=())
        self.cp = None
        self.copy_metadata = None
        self.tracks_2_copy = []

        # Scrolled Window
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)

        # Tracks default
        tracks = None
        try:
            self.disc_tracks = os.listdir(local_mount_point)
        except FileNotFoundError:
            Dialog("No Disc Found", "Please insert a disc and reload Metadata").error_dialog()
            return

        # Write to Entries
        if self.metadata is not None:
            artist_entry.set_text(self.metadata.get_artist())
            album_entry.set_text(self.metadata.get_album())

            # Metadata append
            tracks = self.metadata.get_tracks()
        self.list_store = Gtk.ListStore(bool, str, str, str)
        try:
            for i in range(len(tracks)):
                self.list_store.append([False, str(i + 1), tracks[i].get_name(), tracks[i].get_artist()])
        except TypeError:
            for j in range(len(self.disc_tracks)):
                self.list_store.append([False, str(j + 1), self.disc_tracks[j], ""])

        tree_view.set_model(self.list_store)

        # Toggle Buttons
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)
        column_toggle = Gtk.TreeViewColumn("Import", renderer_toggle, active=0)
        tree_view.append_column(column_toggle)

        # Track Numbers
        renderer_track_number = Gtk.CellRendererText()
        column_track_number = Gtk.TreeViewColumn("Nr.", renderer_track_number, text=1)
        tree_view.append_column(column_track_number)
        renderer_track_number.connect("edited", self.text_edited)

        # Audio Titles
        renderer_title = Gtk.CellRendererText()
        renderer_title.set_property("editable", True)
        column_title = Gtk.TreeViewColumn("Title", renderer_title, text=2)
        tree_view.append_column(column_title)
        renderer_title.connect("edited", self.text_edited2)

        # Audio Artists
        renderer_artist = Gtk.CellRendererText()
        renderer_artist.set_property("editable", True)
        column_artist = Gtk.TreeViewColumn("Artist", renderer_artist, text=3)
        tree_view.append_column(column_artist)
        renderer_artist.connect("edited", self.text_edited3)

    def text_edited(self, widget, path, text):
        self.list_store[path][1] = text

    def on_cell_toggled(self, widget, path):
        self.list_store[path][0] = not self.list_store[path][0]

    def text_edited2(self, widget, path, text):
        self.list_store[path][2] = text

    def text_edited3(self, widget, path, text):
        self.list_store[path][3] = text

    @staticmethod
    def return_info(tracks):
        return CDInfo(album_entry.get_text(), artist_entry.get_text(), tracks)

    def on_copy_clicked(self):
        title_numbers = os.listdir(local_mount_point)
        tracks = []
        for i in range(len(self.list_store)):
            if self.list_store[i][0]:
                self.tracks_2_copy.append(title_numbers[i])
                tracks.append(TrackInfo(self.list_store[i][2], None, None, self.list_store[i][3]))
        self.copy_metadata = self.return_info(tracks)
        self.rip()

    def execute_copy(self):
        global is_running
        print("CopyStart")
        info = Preparer().return_all()
        print(info)
        listener = MyCopyListener()
        try:
            self.cp = CopyProcessor(info[0], info[1], info[2], listener, self.copy_metadata, self.tracks_2_copy)
            self.cp.run()
        except RipperError as error:
            print("An Error has occurred: ", error.reason.to_string())
            GLib.idle_add(Dialog(error.reason.to_string(), error.text).error_dialog)
        self.t = Thread(target=self.execute_copy, args=())
        if eject_standard.get_active() == 1:
            os.system("eject")
        GLib.idle_add(self.update_ui, "Copy", 0, "")
        is_running = False

    @staticmethod
    def update_ui(copy_button_title, fraction, filename_label_text):
        # Dialog.finished_dialog()
        Dialog.notify()
        copyButton.set_label(copy_button_title)
        progressbar.set_fraction(fraction)
        filename_label.set_text(filename_label_text)

    def rip(self):
        if os.path.isdir(local_mount_point):
            if format_chooser.get_active_text() != "":
                path = output.get_text()
                if os.path.isdir(path):
                    self.t.start()
                    copyButton.set_label("Cancel")
                    return
                else:
                    directory_error.format_secondary_text(path + "\n")
                    directory_error.run()
        else:
            print("No Device found")
            Dialog("No Disc Found", "Please insert a disc").error_dialog()

    def kill_process(self):
        self.cp.stop_copy()
        self.t.join()
        copyButton.set_label("Copy")
        progressbar.set_fraction(0)
        filename_label.set_text("")
        self.t = Thread(target=self.execute_copy, args=())


class MyCopyListener(CopyProcessorListener):
    @staticmethod
    def on_copy_item(count):
        percentage = 1 / count
        progressbar.set_fraction(progressbar.get_fraction() + percentage)

    @staticmethod
    def on_filename(file):
        filename_label.set_text("Processing: %s" % file)


class Handler:

    def __init__(self):
        global metadata_view
        self.player = Player(self.refresh_button)
        self.player.set_file(local_mount_point + "/" + metadata_view.disc_tracks[0])
        self.slider_handler_id = slider.connect("value-changed", self.on_slider_seek)

    @staticmethod
    def ok_button_clicked(button):
        directory_error.hide()

    @staticmethod
    def on_copy_button_clicked(button):
        global is_running
        if os.path.isdir(local_mount_point):
            if format_chooser.get_active_text() != "":
                if os.path.isdir(output.get_text()):
                    if not is_running:
                        is_running = True
                        metadata_view.on_copy_clicked()
                    else:
                        metadata_view.kill_process()
                        is_running = False

                else:
                    directory_error.format_secondary_text(output.get_text() + "\n")
                    directory_error.run()
        else:
            print("No Device found")
            Dialog("No Disc Found", "Please insert a disc").error_dialog()

    @staticmethod
    def search_button3_clicked(button):
        ui_objects = UiObjects()
        folder = ui_objects.chooser()
        standard_output_entry.set_text(folder)

    @staticmethod
    def search_button2_clicked(button):
        ui_objects = UiObjects()
        folder = ui_objects.chooser()
        if folder is not None:
            output.set_text(folder)

    def player_button_clicked(self, button):
        if player_button.get_image() == play_image:
            player_button.set_image(pause_image)
            self.player.play()
            GLib.timeout_add(1000, self.update_slider)
        else:
            player_button.set_image(play_image)
            self.player.pause()

    def update_slider(self):
        if not self.player.is_playing:
            return False
        else:
            slider.set_range(0, self.player.get_duration())
            slider.handler_block(self.slider_handler_id)
            slider.set_value(self.player.get_position())
            slider.handler_unblock(self.slider_handler_id)

            return True

    def on_slider_seek(self, argument):
        seek_time_secs = slider.get_value()
        self.player._player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                        seek_time_secs * Gst.SECOND)

    def volume_changed(self, button, volume):
        self.player.set_volume(volume)

    @staticmethod
    def refresh_button(player):
        player_button.set_image(play_image)

    def tree_view_columns_changed(self, widget, row, column):
        print("Changed row: ", row)
        self.player.reset()
        index = int(row.get_indices()[0])
        self.player.set_file(local_mount_point + "/" + metadata_view.disc_tracks[index])
        player_button.set_image(pause_image)
        self.player.play()

    @staticmethod
    def setting_button_clicked(button):
        settings_window.show_all()
        with open("settings.yaml") as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)
            if settings['always_eject']:
                eject_standard.set_active(True)
            if settings['autodetect']:
                auto_detect.set_active(True)
            if settings['outputFolder'] != '':
                standard_output_entry.set_text(str(settings['outputFolder']))
            if settings['standardFormat'] is not None:
                for i in range(0, len(formats) - 1):
                    if settings['standardFormat'] == formats[i]:
                        standard_format.set_active(i)

    @staticmethod
    def cancel_button_clicked(button):
        settings_window.hide()

    @staticmethod
    def refresh_button_clicked(button):
        pass

    @staticmethod
    def eject_button_clicked(button):
        os.system("eject")

    @staticmethod
    def apply_button_clicked(button):
        with open("settings.yaml") as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)

        settings['autodetect'] = auto_detect.get_active()

        with open("settings.yaml", "w") as f:
            yaml.dump(settings, f)

        settings['always_eject'] = eject_standard.get_active()

        with open("settings.yaml", "w") as f:
            yaml.dump(settings, f)

        settings['outputFolder'] = standard_output_entry.get_text()

        with open("settings.yaml", "w") as f:
            yaml.dump(settings, f)

        settings['standardFormat'] = standard_format.get_active_text()

        with open("settings.yaml", "w") as f:
            yaml.dump(settings, f)

        settings_window.hide()

        Loader.load_settings()


builder = Gtk.Builder()
builder.add_from_file("data/cd.glade")

output = builder.get_object("output_entry")
filename_label = builder.get_object("label1")
progressbar = builder.get_object("progressbar")
format_chooser = builder.get_object("format_chooser")
settings_window = builder.get_object("settings_window")
auto_detect = builder.get_object("auto_detect")
eject_standard = builder.get_object("eject_standard")
standard_format = builder.get_object("standard_format")
standard_output_entry = builder.get_object("standard_output_entry")
copyButton = builder.get_object("copy_button")
directory_error = builder.get_object("dir_win")
directory_create = builder.get_object("directory_create")
album_create = builder.get_object("album_create")
metadata_win = builder.get_object("metadata_window")
tree_view = builder.get_object("tree_view")
scrolled = builder.get_object("scrolled")
artist_entry = builder.get_object("artist_entry")
album_entry = builder.get_object("album_entry")
player_button = builder.get_object("player_button")
volume = builder.get_object("volume")
slider = builder.get_object("slider")
play_image = builder.get_object("play_image")
pause_image = builder.get_object("pause_image")

metadata_view = MetadataTreeview()

builder.connect_signals(Handler())

window = builder.get_object("main_window")
window.connect("destroy", Gtk.main_quit)
load = Loader()
load.load_formats(formats)
load.load_settings()
window.show_all()
Gtk.main()

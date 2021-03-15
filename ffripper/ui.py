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
from threading import Thread
from rich.traceback import install
from ffripper.process_launcher import CopyProcessor, CopyProcessorListener
from ffripper.errors import RipperError
from ffripper.metadata import Metadata
from ffripper.cdrom_info_object import CDInfo
from ffripper.track_info import TrackInfo
from ffripper.player import Player
from ffripper.ui_elements import UiObjects, Dialog, GladeWindow
from ffripper.image import Image
from ffripper.settings import Settings
from ffripper.logger import logger
from ffripper.disc import Disc
from ffripper.preset import formats

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gst


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
        settings = Settings("../data/settings.yaml")
        if settings.get_output_folder() != '':
            window.output_entry.set_text(settings.get_output_folder())
        if settings.get_default_format() is not None:
            for i in range(len(formats) - 1):
                if settings.get_default_format() == formats[i]:
                    window.format_chooser.set_active(i)


class Preparer:

    def __init__(self, ):
        self.input_dev = window.disc.mount_point
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
        self.is_running = False
        self.disc = Disc()
        self.list_store = Gtk.ListStore(bool, str, str, str, str)
        self.tracks_2_copy = []
        self.copy_metadata = None
        self.copy = None
        self.settings = Settings("../data/settings.yaml")
        self.metadata = None
        self.get_metadata()
        self.thread = Thread(target=self.execute_copy, args=())
        self.cover_art = False
        self.disc_tracks = None
        self.column_toggle = None
        self.create_treeview()
        self.set_cover_image()
        self.set_treeview_content()

        self.widget = builder.get_object('main_window')
        self.player = Player(self.refresh_button)
        self.set_player()
        GladeWindow.connect_signals()
        self.widget.connect("destroy", Gtk.main_quit)
        self.widget.show_all()

    def __getattr__(self, attribute):
        """ Allow direct use of window widget. """
        widget = self.builder.get_object(attribute)
        if widget is None:
            raise AttributeError('Widget \'%s\' not found' % attribute)
        self.__dict__[attribute] = widget  # cache result
        return widget

    def get_metadata(self):
        try:
            self.metadata = Metadata()
        except RipperError as error:
            Dialog(error.reason, error.text).error_dialog()

    def create_treeview(self):
        self.__create_toggle_column()
        self.__create_track_number_column()
        self.__create_title_column()
        self.__create_artist_column()
        self.__create_year_column()
        self.column_toggle.set_clickable(True)
        self.column_toggle.set_widget(self.toggle_all_check_button)

    def __create_toggle_column(self):
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)
        self.column_toggle = Gtk.TreeViewColumn("Import", renderer_toggle, active=0)
        self.tree_view.append_column(self.column_toggle)

    def __create_track_number_column(self):
        renderer_track_number = Gtk.CellRendererText()
        column_track_number = Gtk.TreeViewColumn("Nr.", renderer_track_number, text=1)
        self.tree_view.append_column(column_track_number)
        renderer_track_number.connect("edited", self.text_edited)

    def __create_title_column(self):
        renderer_title = Gtk.CellRendererText()
        renderer_title.set_property("editable", True)
        column_title = Gtk.TreeViewColumn("Title", renderer_title, text=2)
        self.tree_view.append_column(column_title)
        renderer_title.connect("edited", self.title_text_edited)

    def __create_artist_column(self):
        renderer_artist = Gtk.CellRendererText()
        renderer_artist.set_property("editable", True)
        column_artist = Gtk.TreeViewColumn("Artist", renderer_artist, text=3)
        self.tree_view.append_column(column_artist)
        renderer_artist.connect("edited", self.artist_text_edited)

    def __create_year_column(self):
        renderer_year = Gtk.CellRendererText()
        renderer_year.set_property("editable", True)
        year_column = Gtk.TreeViewColumn("Year", renderer_year, text=4)
        self.tree_view.append_column(year_column)
        renderer_year.connect("edited", self.year_edited)

    def set_player(self):
        if self.is_disc():
            self.player.set_file(self.disc.mount_point + "/" + self.disc_tracks[0])

    @staticmethod
    def on_toggle_all():
        pass

    def set_cover_image(self):
        try:
            if (self.metadata.get_cover() != "") and (self.metadata.get_cover() is not None):
                self.cover_art = True
                self.cover_image.set_from_pixbuf(Image.bytes2pixbuf(self.metadata.get_cover()))
        except AttributeError as e:
            logger.error(e)

    def set_treeview_content(self):
        tracks = None
        if self.get_tracks_on_disc():
            if self.metadata is not None:
                self.artist_entry.set_text(self.metadata.get_artist())
                self.album_entry.set_text(self.metadata.get_album())

                tracks = self.metadata.get_tracks()
            try:
                for i in range(len(tracks)):
                    self.list_store.append([True, str(i + 1), tracks[i].get_name(),
                                            tracks[i].get_artist(), tracks[i].get_year()])
            except TypeError:
                for j in range(len(self.disc_tracks)):
                    self.list_store.append([False, str(j + 1), self.disc_tracks[j], "", ""])

            self.tree_view.set_model(self.list_store)

    def get_tracks_on_disc(self):
        try:
            self.disc_tracks = os.listdir(self.disc.mount_point)
            return True
        except FileNotFoundError:
            self.nodiscdialog.run()
            return False

    def text_edited(self, widget, path, text):
        self.list_store[path][1] = text

    def on_cell_toggled(self, widget, path):
        self.list_store[path][0] = not self.list_store[path][0]

    def title_text_edited(self, widget, path, text):
        self.list_store[path][2] = text

    def artist_text_edited(self, widget, path, text):
        self.list_store[path][3] = text

    def year_edited(self, widget, path, text):
        self.list_store[path][4] = text

    def return_info(self, tracks):
        return CDInfo(self.album_entry.get_text(), self.artist_entry.get_text(), tracks, None)

    def execute_copy(self):
        info = Preparer().return_all()
        listener = MyCopyListener()
        cover = None
        try:
            if self.cover_art:
                cover = Image.bytes2png(self.metadata.get_cover(), info[1], "cover")
            self.copy = CopyProcessor(info[0], info[1], info[2], listener, self.copy_metadata, self.tracks_2_copy,
                                      cover)
            self.copy.run()
        except RipperError as error:
            logger.warn("An Error has occurred: ", error.reason.to_string())
            GLib.idle_add(Dialog(error.reason.to_string(), error.text).error_dialog)
        self.thread = Thread(target=self.execute_copy, args=())
        if self.eject_standard.get_active() == 1:
            os.system("eject")
        GLib.idle_add(self.update_ui, "Rip", 0)
        self.is_running = False

    def update_ui(self, copy_button_title, fraction):
        Dialog.notify()
        self.copy_button.set_label(copy_button_title)
        self.progressbar.set_fraction(fraction)
        self.tracks_2_copy = []

    def rip(self):
        if self._check_for_valid_config():
            path = self.output_entry.get_text()
            if os.path.isdir(path):
                self.thread.start()
                self.copy_button.set_label("Cancel")
                return
            else:
                self.directory_error.format_secondary_text(path + "\n")
                self.directory_error.run()

    def kill_process(self):
        self.copy.stop_copy()
        self.thread.join()
        self.copy_button.set_label("Rip")
        self.progressbar.set_fraction(0)
        self.thread = Thread(target=self.execute_copy, args=())

    @staticmethod
    def on_nodiscdialog_response(*args):
        Gtk.main_quit()

    def on_ok_button_clicked(self, button):
        self.directory_error.hide()

    def on_copy_button_clicked(self, button):
        if not self._check_for_valid_config():
            return
        if os.path.isdir(self.output_entry.get_text()):
            if not self.is_running:
                self.is_running = True
                title_numbers = os.listdir(self.disc.mount_point)
                tracks = []
                for i in range(len(self.list_store)):
                    if self.list_store[i][0]:
                        self.tracks_2_copy.append(title_numbers[i])
                        tracks.append(TrackInfo(self.list_store[i][2], None,
                                                self.list_store[i][4], self.list_store[i][3]))
                self.copy_metadata = self.return_info(tracks)
                self.rip()
            else:
                self.kill_process()
                self.is_running = False

        else:
            self.directory_error.format_secondary_text(self.output_entry.get_text() + "\n")
            self.directory_error.run()

    def _check_for_valid_config(self):
        return bool(self.is_disc() and self.format_chooser.get_active_text() != "")

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
        slider_handler_id = self.slider.connect("value-changed", self.on_slider_seek)
        if not self.player.is_playing:
            return False
        self.slider.set_range(0, self.player.get_duration())
        self.slider.handler_block(slider_handler_id)
        self.slider.set_value(player.get_position())
        self.slider.handler_unblock(slider_handler_id)

        return True

    def on_slider_seek(self, argument):
        seek_time_secs = self.slider.get_value()
        self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                seek_time_secs * Gst.SECOND)

    def on_volume_changed(self, button, volume):
        self.player.set_volume(volume)

    def on_retry_clicked(self, *args):
        self.nodiscdialog.hide()
        self.update_metadata()
        self.set_cover_image()
        self.set_treeview_content()

    def refresh_button(self, player):
        self.player_button.set_image(self.play_image)

    def on_tree_view_columns_changed(self, widget, row, column):
        logger.debug("Changed row: ", row)
        self.player.reset()
        index = int(row.get_indices()[0])
        self.player.set_file(self.disc.mount_point + "/" + self.disc_tracks[index])
        self.player_button.set_image(self.pause_image)
        self.player.play()

    def on_setting_button_clicked(self, button):
        self.settings_window.show_all()
        self.eject_standard.set_active(self.settings.get_eject())
        self.standard_output_entry.set_text(str(self.settings.get_output_folder()))
        if self.settings.get_default_format() is not None:
            for i in range(len(formats) - 1):
                if self.settings.get_default_format() == formats[i]:
                    self.standard_format.set_active(i)

    def on_cancel_button_clicked(self, button):
        self.settings_window.hide()

    def on_refresh_button_clicked(self, button):
        self.update_metadata()
        self.set_treeview_content()

    @staticmethod
    def on_eject_button_clicked(button):
        os.system("eject")

    def on_apply_button_clicked(self, button):
        self.settings.set_eject(self.eject_standard.get_active())
        self.settings.set_output_folder(self.standard_output_entry.get_text())
        self.settings.set_default_format(self.standard_format.get_active_text())
        self.settings.apply_changes()
        self.settings_window.hide()

        Loader.load_settings()

    def on_about_clicked(self, button):
        about = self.about_dialog
        about.set_transient_for(self.widget)
        about.run()

    def on_aboutdialog_response(self, *args):
        self.about_dialog.hide()

    def on_theme_changed(self, widget):
        self.settings.set_theme(widget.get_active_text())

    def update_metadata(self):
        self.get_metadata()

    def is_disc(self):
        if os.path.isdir(self.disc.mount_point):
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
    logger.info("Started FFRipper")
    Gtk.main()

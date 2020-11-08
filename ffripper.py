#! /usr/bin/env python3

import os
import gi
import yaml
from threading import Thread
from process_launcher import CopyProcessor, CopyProcessorListener
from errors import RipperError
from metadata import Metadata
from cdrom_info_object import CDInfo
from track_info import TrackInfo
# from player import Player

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

gi.require_version('Notify', '0.7')
from gi.repository import Notify

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
        if always_eject:
            eject.set_active(True)
        elif not always_eject:
            eject.set_active(False)
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
        self.eject = eject.get_active()
        self.output_folder = output.get_text()

    def return_all(self):
        prepared_list = [self.input_dev, self.output_folder, self.format]
        return prepared_list


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


class MetadataEditor(Gtk.Window):

    def __init__(self, metadata):
        self.metadata = metadata
        self.t = Thread(target=self.execute_copy, args=())
        self.cp = None
        self.copy_metadata = None
        self.tracks_2_copy = []
        # Window
        Gtk.Window.__init__(self, title="FFRipper")

        # Scrolled Window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(350)

        # Main Box
        self.box = Gtk.Box.new(1, 0)
        self.add(self.box)

        # Artist Box
        box_double = Gtk.Box.new(0, 0)
        label = Gtk.Label()
        label.set_text("Artist: ")
        box_double.pack_start(label, True, True, 5)

        self.artist_entry = Gtk.Entry()
        self.artist_entry.set_text(self.metadata.get_artist())
        box_double.pack_start(self.artist_entry, True, True, 5)

        self.box.pack_start(box_double, True, True, 5)

        # Album Box
        box_double = Gtk.Box.new(0, 0)
        label = Gtk.Label()
        label.set_text("Album: ")
        box_double.pack_start(label, True, True, 5)

        self.album_entry = Gtk.Entry()
        self.album_entry.set_text(self.metadata.get_album())
        box_double.pack_start(self.album_entry, True, True, 5)

        self.box.pack_start(box_double, True, True, 5)

        # Metadata append
        tracks = self.metadata.get_tracks()
        self.list_store = Gtk.ListStore(bool, str, str, str)
        try:
            for i in range(len(tracks)):
                self.list_store.append([False, str(i + 1), tracks[i].get_name(), self.metadata.get_artist()])
        except TypeError:
            disc_tracks = os.listdir(local_mount_point)
            for j in range(len(disc_tracks)):
                self.list_store.append([False, str(j + 1), disc_tracks[j], ""])

        self.tree_view = Gtk.TreeView(model=self.list_store)

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
        renderer_title.connect("edited", self.text_edited2)

        # Audio Artists
        renderer_artist = Gtk.CellRendererText()
        renderer_artist.set_property("editable", True)
        column_artist = Gtk.TreeViewColumn("Artist", renderer_artist, text=3)
        self.tree_view.append_column(column_artist)
        renderer_artist.connect("edited", self.text_edited3)

        # Insert into Box
        scrolled.add(self.tree_view)
        self.box.pack_start(scrolled, True, True, 5)

        # The Audio Player Box
        box_double = Gtk.Box.new(0, 0)
        start_pause_button = Gtk.Button

        # Action Buttons
        box_double = Gtk.Box.new(0, 0)
        button = Gtk.Button.new_with_label("Copy")
        button.connect("clicked", self.on_copy_clicked)
        box_double.pack_start(button, True, True, 5)

        self.box.pack_start(box_double, True, True, 5)

    def text_edited(self, widget, path, text):
        self.list_store[path][1] = text

    def on_cell_toggled(self, widget, path):
        self.list_store[path][0] = not self.list_store[path][0]

    def text_edited2(self, widget, path, text):
        self.list_store[path][2] = text

    def text_edited3(self, widget, path, text):
        self.list_store[path][3] = text

    def return_info(self, tracks):
        return CDInfo(self.album_entry.get_text(), self.artist_entry.get_text(), tracks)

    def on_copy_clicked(self, button):
        title_numbers = os.listdir(local_mount_point)
        tracks = []
        for i in range(len(self.list_store)):
            if self.list_store[i][0]:
                self.tracks_2_copy.append(title_numbers[i])
                tracks.append(TrackInfo(self.list_store[i][2], None, None, None))
        self.copy_metadata = self.return_info(tracks)
        self.rip()

    def execute_copy(self):
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
        if eject.get_active() == 1:
            os.system("eject")
        GLib.idle_add(self.update_ui, "Copy", 0, "")

    @staticmethod
    def update_ui(copy_button_title, fraction, filename_label_text):
        # Dialog.finished_dialog()
        Dialog.notify()
        copyButton.set_label(copy_button_title)
        progressbar.set_fraction(fraction)
        filename_label.set_text(filename_label_text)

    def rip(self):
        self.destroy()
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
            "Process finished in: ..."
        )
        dialog.run()
        dialog.destroy()

    @staticmethod
    def notify():
        Notify.init("FFRipper")
        notification = Notify.Notification.new(
            "Finished Ripping",
            "Process finished in: ..."
        )
        notification.show()


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
        self.is_running = False
        self.metadata_editor = None

    @staticmethod
    def ok_button_clicked(button):
        directory_error.hide()

    def on_copy_button_clicked(self, button):
        if os.path.isdir(local_mount_point):
            if format_chooser.get_active_text() != "":
                if os.path.isdir(output.get_text()):
                    if not self.is_running:
                        metadata = None
                        try:
                            metadata = Metadata()
                        except RipperError:
                            print("ErrorFound")
                        self.metadata_editor = MetadataEditor(metadata)
                        self.metadata_editor.show_all()
                        self.is_running = True
                    else:
                        self.metadata_editor.kill_process()
                        self.is_running = False

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
builder.add_from_file("cd.glade")
builder.connect_signals(Handler())

window = builder.get_object("main_window")
window.connect("destroy", Gtk.main_quit)

output = builder.get_object("output_entry")
eject = builder.get_object("eject_button")
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

load = Loader()
load.load_formats(formats)
load.load_settings()
window.show_all()
Gtk.main()

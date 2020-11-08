#!/usr/bin/env python3

import os
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)


class Player:

    def __init__(self):
        self.filepath = ""
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def set_file(self, filepath: str):
        self.filepath = filepath
        self.player.set_property("uri", "file://" + self.filepath)

    def play(self):
        if os.path.isfile(self.filepath):
            self.player.set_state(Gst.State.PLAYING)
        else:
            self.player.set_state(Gst.State.NULL)
            print("Can not find file on audio-CD")

    def pause(self):
        self.player.set_state(Gst.State.PAUSED)

    def reset(self):
        self.player.set_state(Gst.State.NULL)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)

    def get_duration(self):
        success, duration = self.player.query_duration(Gst.Format.TIME)
        if success:
            duration = duration / Gst.SECOND
        else:
            raise LookupError
        return duration

    def get_position(self):
        success, position = self.player.query_position(Gst.Format.TIME)
        if not success:
            raise Exception("Couldn't fetch current song position to update slider")
        else:
            position = float(position) / Gst.SECOND
        return position


player = Player()
player.set_file("/home/stefan/Musik/TestFolder/Mica țiganiadă.ogg")
player.play()
input(":: ")
print(player.get_duration())
print(player.get_position())
player.pause()
input("::")
player.play()
input("::")

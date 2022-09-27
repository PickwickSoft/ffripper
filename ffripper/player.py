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

import os
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)


class Player:
    """
    The Player for FFRipper.
    """

    def __init__(self, handler):
        """
        Constructs the player object.
        :param handler: method or function
        """
        self.handler = handler
        self.filepath = ""
        self._player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self._player.set_property("video-sink", fakesink)
        bus = self._player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.__on_message)
        self._player.connect("about-to-finish", self.handler)
        self.is_playing = False
        self.duration = 0

    def set_file(self, filepath: str):
        """
        Set file to be played
        :param filepath: str (path to audio file)
        """
        self.filepath = filepath
        self._player.set_property("uri", f"file://{self.filepath}")

    def set_volume(self, volume):
        """
        Set volume for player
        :param volume: float between 0.0, representing mute and 1.0 representing maximal volume
        """
        self._player.set_property('volume', volume)

    def play(self):
        """
        Starts playing. Before running this you need to call *set_file()*.
        Make sure you have set a file.
        """
        if os.path.isfile(self.filepath):
            self._player.set_state(Gst.State.PLAYING)
            self.is_playing = True
        else:
            self._player.set_state(Gst.State.NULL)
            print("Can not find file on audio-CD")

    def pause(self):
        """
        Pauses the player. Play on calling the *play()* method
        """
        self._player.set_state(Gst.State.PAUSED)
        self.is_playing = False

    def reset(self):
        """
        Stops current stream and resets the player. *Attention, you need to call set_file()
        to play again*
        """
        self._player.set_state(Gst.State.NULL)
        self.is_playing = False


    def __on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self._player.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            self._player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print(f"Error: {err}", debug)

    def get_duration(self):
        """
        Returns the length of set track
        :return: int
        """
        if self.duration == 0:
            while True:
                success, duration = self._player.query_duration(Gst.Format.TIME)
                if success:
                    duration = duration / Gst.SECOND
                    break
            if not success:
                raise LookupError
        else:
            duration = self.duration
        return duration

    def get_position(self):
        """
        Returns the current position
        :return: int
        """
        while True:
            success, position = self._player.query_position(Gst.Format.TIME)
            if success:
                position = float(position) / Gst.SECOND
                break
        if not success:
            raise Exception("Couldn't fetch current song position to update slider")
        return position

    def seek_simple(self, *args):
        """
        Changes the playing location. Same Arguments as for Gst.PlayBin required.
        :param args:
        :return:
        """
        self._player.seek_simple(*args)

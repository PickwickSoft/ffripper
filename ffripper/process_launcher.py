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

import abc
import subprocess
import time
import shlex
from ffripper.errors import Reason, RipperError


class CopyProcessorListener(abc.ABC):

    def on_copy_item(self, count):
        pass

    def on_filename(self, file):
        pass


class CopyProcessor:

    def __init__(self, input_location, output_location, file_format, listener, metadata, audio_files, cover):
        self.input_location = input_location
        self.output_location = output_location
        self.format = file_format
        self.audio_files = audio_files
        self.audio_files = self.file_filter(self.audio_files)
        self.should_continue = True
        self.listener = listener
        self.meta = metadata
        self.track_info = self.meta.get_tracks()
        self.processes = []
        self.cover = cover

    def stop_copy(self):
        self.should_continue = False
        for i in range(len(self.processes)):
            print("Terminating Process %d" % i)
            self.processes[i].kill()
            print("Process %d Closed" % i)

    @staticmethod
    def file_filter(listed_dir):
        return [
            listed_dir[i]
            for i in range(len(listed_dir))
            if listed_dir[i].endswith('.wav')
        ]

    def run(self):
        files = len(self.audio_files)
        start_time = []
        for i in range(len(self.audio_files)):
            if not self.should_continue:
                return
            track_info = self.track_info[i]
            current_audio_file = "{0}.{1}".format(track_info.get_name(), self.format)
            self.listener.on_filename(track_info.get_name())
            start_time.append(time.time())
            print(time.time(), ": starting subprocess ", i)
            rip_command = "ffmpeg -y -i \"{0}/{1}\" -i \"{2}\" -metadata title=\"{3}\" " \
                          "-metadata artist=\"{4}\" -metadata album=\"{5} \" \"{6}/{7}\"".format(self.input_location,
                                                                                                 self.audio_files[i],
                                                                                                 self.cover,
                                                                                                 track_info.get_name(),
                                                                                                 track_info.get_artist(),
                                                                                                 self.meta.get_album(),
                                                                                                 self.output_location,
                                                                                                 current_audio_file)
            try:
                print(rip_command)
                ffmpeg = subprocess.Popen(shlex.split(rip_command), stderr=subprocess.STDOUT)
            except:
                raise RipperError(Reason.FFMPEGERROR, "An Error occurred while running FFMPEG")
            self.processes.append(ffmpeg)

        for j in range(len(self.processes)):
            self.processes[j].wait()
            print("Process ", j, " finished after: ", time.time() - start_time[j])
            self.listener.on_copy_item(files)
        # print('\n\nWait!\n\n')elapsedTime
        self.listener.on_filename("Done")

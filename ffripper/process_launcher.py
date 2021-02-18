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
from ffripper.extended_subprocess import PopenFinishedCallback


class CopyProcessorListener(abc.ABC):

    def on_copy_item(self, count):
        pass

    def on_filename(self, file):
        pass


class CopyProcessor:

    def __init__(self, input_location, output_location, file_format, listener, metadata, audio_files, cover):
        self.finished_processes = 0
        self.input_location = input_location
        self.output_location = output_location
        self.format = file_format
        self.audio_files = self.filter_files_by_extension(audio_files, '.wav')
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
    def filter_files_by_extension(listed_dir, extension):
        return [
            listed_dir[i]
            for i in range(len(listed_dir))
            if listed_dir[i].endswith(extension)
        ]

    def run(self):
        start_time = []
        for i in range(len(self.audio_files)):
            if not self.should_continue:
                return
            start_time.append(time.time())
            print(time.time(), ": starting subprocess ", i)
            cover_art_stream = (
                "" if self.cover is None else "-i \"{0}\"".format(self.cover)
            )

            rip_command = """ffmpeg -y -threads 0 -i \"{0}/{1}\" {2} -metadata title=\"{3}\"  -metadata artist=\"{4}\" 
                            -metadata album=\"{5}\" -metadata date=\"{6}\" \"{7}/{8}\"""".format(
                self.input_location,
                self.audio_files[i],
                cover_art_stream,
                self.track_info[i].get_name(),
                self.track_info[i].get_artist(),
                self.meta.get_album(),
                self.track_info[i].get_year(),
                self.output_location,
                "{0}.{1}".format(
                    self.track_info[i].get_name(),
                    self.format))
            try:
                print(rip_command)
                ffmpeg = subprocess.Popen(shlex.split(rip_command), stderr=subprocess.STDOUT)
            except:
                raise RipperError(Reason.FFMPEGERROR, "An Error occurred while running FFMPEG")
            self.processes.append(ffmpeg)
        self.wait_for_finish()

    def wait_for_finish(self):
        while self.finished_processes != len(self.audio_files):
            for i in self.processes:
                PopenFinishedCallback(i, self.on_finished)

    def on_finished(self):
        self.finished_processes += 1
        self.listener.on_copy_item(len(self.audio_files))

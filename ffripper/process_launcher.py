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
import abc
import subprocess
import time
import shlex
from ffripper.errors import Reason, RipperError
from ffripper.utils import is_installed
from ffripper.progress import FFmpegProgress
from ffripper.logger import logger


class CopyProcessorListener(abc.ABC):

    @staticmethod
    def on_copy_item(count):
        pass

    @staticmethod
    def on_filename(file):
        pass


class CopyProcessor:

    def __init__(self, input_location, output_location, file_format, listener, metadata, audio_files, cover,
                 album_directory=True, artist_directory=True):
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
        self.album_directory = album_directory
        self.artist_directory = artist_directory
        self.base_location = output_location

    def create_album_directory(self):
        if self.album_directory:
            self.output_location = os.path.join(self.output_location, self.meta.get_album())
            logger.info("Creating Path {}".format(
                self.output_location
            ))
            self.mkdir(self.output_location)

    def create_artist_directory(self):
        if self.artist_directory:
            self.output_location = os.path.join(self.output_location, self.meta.get_artist())
            logger.info("Creating Path {}".format(
                self.output_location
            ))
            self.mkdir(self.output_location)

    @staticmethod
    def mkdir(path):
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

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
        logger.info("Started at {}".format(time.time()))
        start_time = []
        self.create_dirs()
        for i in range(len(self.audio_files)):
            if not self.should_continue:
                return
            start_time.append(time.time())
            logger.debug("{}: starting subprocess {}".format(time.time(), i))
            cover_art_stream = (
                "" if self.cover is None else "-i \"{0}\"".format(self.cover)
            )
            ffmpeg_path = is_installed("ffmpeg")
            rip_command = """{0} -y -threads 0 -i \"{1}/{2}\" {3} -metadata title=\"{4}\"  -metadata artist=\"{5}\" 
                            -metadata album=\"{6}\" -metadata date=\"{7}\" \"{8}/{9}\"""".format(
                ffmpeg_path,
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
                logger.debug(rip_command)
                ffmpeg = subprocess.Popen(shlex.split(rip_command),
                                          stderr=subprocess.STDOUT,
                                          stdout=subprocess.PIPE
                                          )
            except:
                raise RipperError(Reason.FFMPEGERROR, "An Error occurred while running FFMPEG")
            self.processes.append(ffmpeg)
        self.wait_for_finish()
        self.rm_cover()

    def wait_for_finish(self):
        while self.finished_processes != len(self.audio_files):
            for i in self.processes:
                FFmpegProgress(i, len(self.audio_files), self.listener.on_copy_item, self.on_finished)

    def on_finished(self):
        self.finished_processes += 1

    def create_dirs(self):
        self.create_artist_directory()
        self.create_album_directory()

    def rm_cover(self):
        path = os.path.join(self.base_location + "/cover.png")
        if os.path.exists(path):  # Else it has been deleted from outside
            os.remove(path)

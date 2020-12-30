import abc
import subprocess
import time
import shlex
from errors import Reason, RipperError


class CopyProcessorListener(abc.ABC):

    def on_copy_item(self, count):
        pass

    def on_filename(self, file):
        pass


class CopyProcessor:

    def __init__(self, input_location, output_location, file_format, listener, metadata, audio_files):
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

    def stop_copy(self):
        self.should_continue = False
        for i in range(0, len(self.processes)):
            print("Terminating Process %d" % i)
            self.processes[i].kill()
            print("Process %d Closed" % i)

    @staticmethod
    def file_filter(listed_dir):
        file_list = []
        for i in range(0, len(listed_dir)):
            if listed_dir[i].endswith('.wav'):
                file_list.append(listed_dir[i])
        return file_list

    def run(self):
        files = len(self.audio_files)
        start_time = []
        for i in range(len(self.audio_files)):
            if not self.should_continue:
                return
            track_info = self.track_info[i]
            current_audio_file = track_info.get_name()
            current_audio_file += "."
            current_audio_file += self.format
            self.listener.on_filename(track_info.get_name())
            start_time.append(time.time())
            print(time.time(), ": starting subprocess ", i)
            rip_command = "ffmpeg -y -i \"{}/{}\" -metadata title=\"{}\" -metadata artist=\"{}\" -metadata album=\"{}" \
                          "\" \"{}/{}\"".format(self.input_location, self.audio_files[i], track_info.get_name(),
                                                self.meta.get_artist(), self.meta.get_album(), self.output_location,
                                                current_audio_file)
            shlex.split(rip_command)
            print(rip_command)
            try:
                ffmpeg = subprocess.Popen(rip_command, stderr=subprocess.STDOUT, shell=True)
            except:
                raise RipperError(Reason.FFMPEGERROR, "An Error occurred while running FFMPEG")
            self.processes.append(ffmpeg)

        for j in range(len(self.processes)):
            self.processes[j].wait()
            print("Process ", j, " finished after: ", time.time() - start_time[j])
            self.listener.on_copy_item(files)
        # print('\n\nWait!\n\n')elapsedTime
        self.listener.on_filename("Done")

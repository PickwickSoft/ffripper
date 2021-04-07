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

import io
import re
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen


def duration_in_seconds(duration):
    """
    Return the number of seconds of duration, an integer.
    Duration is a string of type hh:mm:ss.ts
    """
    duration = duration.split('.')[0]  # get rid of milliseconds
    hours, mins, secs = [int(i) for i in duration.split(':')]
    return secs + (hours * 3600) + (mins * 60)


class FFmpegProgress:

    def __init__(self, process: Popen, total_processes: int, listener, finished_call) -> None:
        self._proc = process
        self._total = total_processes
        self._listener = listener
        self._finished = finished_call
        with ThreadPoolExecutor() as executor:
            executor.submit(self.parse_output)

    def parse_output(self):
        final_output = myline = ''
        old_percentage = 0
        reader = io.TextIOWrapper(self._proc.stdout, encoding='utf8')
        while True:
            out = reader.read(1)
            if out == '' and self._proc.poll() is not None:
                break
            myline += out
            if out in ('\r', '\n'):
                m = re.search("Duration: ([0-9:.]+)", myline)
                if m:
                    total = duration_in_seconds(m.group(1))
                n = re.search("time=([0-9:]+)", myline)
                # time can be of format 'time=hh:mm:ss.ts' or 'time=ss.ts'
                # depending on ffmpeg version
                if n:
                    time = n.group(1)
                    if ':' in time:
                        time = duration_in_seconds(time)
                    now_sec = int(float(time))
                    try:
                        percentage = 100 * now_sec / total / self._total
                        self._listener(percentage - old_percentage)
                        old_percentage = percentage
                    except (UnboundLocalError, ZeroDivisionError):
                        pass
                final_output += myline
                myline = ''
        self._finished()

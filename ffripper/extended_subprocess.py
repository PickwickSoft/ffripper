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

from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen
from typing import Callable


class PopenFinishedCallback:
    """Finished Callback for subprocess.Popen"""

    def __init__(self, subprocess: Popen, callback: Callable) -> None:
        self._proc = subprocess
        self._callback = callback
        with ThreadPoolExecutor() as executor:
            executor.submit(self._run)

    def _run(self):
        self._proc.wait()
        self._callback()

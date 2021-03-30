#   ffripper-0.1 - Audio-CD ripper.
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

from ffripper.errors import RipperError, Reason


def is_installed(program):
    """
    If program is a program name, returns the absolute path to this program if
    included in the PATH enviromental variable, else empty string.
    If program is an absolute path, returns the path if it's executable, else
    empty sring.
    """
    program = os.path.expanduser(program)
    for path in os.getenv('PATH').split(os.pathsep):
        fpath = os.path.join(path, program)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return fpath
    raise RipperError(Reason.FFMPEGNOTINSTALLED, "Please install ffmpeg and try again")

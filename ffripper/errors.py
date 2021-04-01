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

from enum import Enum


class RipperError(Exception):

    def __init__(self, reason, text):
        self.reason = reason
        self.text = text


class Reason(Enum):
    UNKNOWNERROR = 0
    NETWORKERROR = 1
    MUSICBRAINZERROR = 2
    METADATANOTFOUNDERROR = 3
    FFMPEGERROR = 4
    NODISCERROR = 5
    PERMISIONERROR = 6
    FFMPEGNOTINSTALLED = 7

    def to_string(self):
        if self == Reason.NETWORKERROR:
            return "Network Error"
        elif self == Reason.METADATANOTFOUNDERROR:
            return "Metadata Not Found Error"
        elif self == Reason.MUSICBRAINZERROR:
            return "Musicbrainz Error"
        elif self == Reason.FFMPEGERROR:
            return "FFMPEG Error"
        elif self == Reason.NODISCERROR:
            return "No Disc Found Error"
        elif self == Reason.PERMISIONERROR:
            return "Permission Denied"
        elif self == Reason.FFMPEGNOTINSTALLED:
            return "FFmpeg is not installed"
        else:
            return "Unknown"

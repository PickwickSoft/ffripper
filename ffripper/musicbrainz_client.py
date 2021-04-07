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

import musicbrainzngs
import discid
import ffripper
from ffripper.errors import RipperError, Reason
from ffripper.logger import logger


class MusicbrainzClient:

    def __init__(self):
        self.id = None

    def get_disk_id(self):
        try:
            disc = discid.read(discid.get_default_device())
            self.id = disc.id
            print(self.id)
        except discid.DiscError:
            logger.warning("No Disc Found")

    def get_metadata(self):
        self.get_disk_id()
        musicbrainzngs.set_useragent(ffripper.__name__, ffripper.__version__)
        try:
            result = musicbrainzngs.get_releases_by_discid(self.id, includes=["recordings", "artists", "recording-rels",
                                                                              "labels", "artist-rels", "release-rels",
                                                                              "work-rels", "aliases", "artist-credits",
                                                                              "release-groups"])
        except musicbrainzngs.musicbrainz.NetworkError as e:
            raise RipperError(Reason.NETWORKERROR, "Problem communicating with the MB server")
        except musicbrainzngs.ResponseError:
            return None
        return result

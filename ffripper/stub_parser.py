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

import musicbrainzngs

from ffripper.cd_info_parser import CdInfoParser
from ffripper.track_info import TrackInfo
from ffripper.cdrom_info_object import CDInfo


class CdStubParser(CdInfoParser):

    def __init__(self, dictionary):
        self.dict = dictionary
        self.artist = ""

    def get_disc_info(self):
        album = self.parse_for_album()
        self.artist = self.parse_for_artist()
        tracks = self.parse_for_tracks()
        cover = self.parse_for_cover()
        return CDInfo(album, self.artist, tracks, cover)

    def parse_for_album(self):
        return self.dict['cdstub']["title"]

    def parse_for_artist(self):
        return self.dict['cdstub']["artist"]

    def parse_for_tracks(self):
        return [
            TrackInfo(
                self.dict['cdstub']["track-list"][i]["title"],
                self.dict['cdstub']["track-list"][i]["length"],
                "",
                self.artist,
            )
            for i in range(len(self.dict['cdstub']["track-list"]))
        ]

    def parse_for_cover(self):
        try:
            return musicbrainzngs.get_image(self.dict['cdstub']['id'], 'front')  # Not working right now: ResponseError
        except musicbrainzngs.ResponseError:
            return ''

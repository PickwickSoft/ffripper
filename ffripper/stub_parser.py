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

from cd_info_parser import CdInfoParser
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
        album = self.dict['cdstub']["title"]
        return album

    def parse_for_artist(self):
        artist = self.dict['cdstub']["artist"]
        return artist

    def parse_for_tracks(self):
        tracks = []
        for i in range(0, len(self.dict['cdstub']["track-list"])):
            tracks.append(TrackInfo(self.dict['cdstub']["track-list"][i]["title"],
                                    self.dict['cdstub']["track-list"][i]["length"], None, self.artist))
        return tracks

    def parse_for_cover(self):
        try:
            return musicbrainzngs.get_image(self.dict['cdstub']['id'], 'front')  # Not working right now: ResponseError
        except musicbrainzngs.ResponseError:
            return ''

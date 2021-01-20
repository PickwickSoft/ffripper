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


class CdDiscParser(CdInfoParser):

    def __init__(self, dictionary):
        self.dict = dictionary
        self.disc_id = self.dict['disc']['id']
        self._mb_id = ""
        self._release = None
        self._album = ""

    def get_disc_info(self):
        tracks = self.parse_for_tracks()
        album = self.parse_for_album()
        self._album = album
        artist = self.parse_for_artist()
        cover = self.parse_for_cover()

        return CDInfo(album, artist, tracks, cover)

    def parse_for_album(self):
        try:
            album = self._release['title']
        except KeyError:
            album = self.dict["disc"]["release-list"][0]["title"]
        return album

    def parse_for_artist(self):
        artist = self.dict["disc"]["release-list"][0]["artist-credit"][0]["artist"]["name"]
        return artist

    def parse_for_tracks(self):
        tracks = []
        try:
            for i in range(len(self.dict['disc']['release-list'][0]['medium-list'])):
                if 0 < len(self.dict['disc']['release-list'][0]['medium-list'][i]['disc-list']):
                    for f in range(len(self.dict['disc']['release-list'][0]['medium-list'][i]['disc-list'])):
                        if self.dict['disc']['release-list'][0]['medium-list'][i]['disc-list'][f]['id'] == self.disc_id:
                            self._mb_id = self.dict['disc']['release-list'][0]['id']
                            self._release = self.dict['disc']['release-list'][0]['medium-list'][i]
                            for j in range(len(self.dict['disc']['release-list'][0]['medium-list'][i]['track-list'])):
                                tracks.append(
                                    TrackInfo(self.dict['disc']['release-list'][0]['medium-list'][i]['track-list'][j]
                                              ['recording']["title"],
                                              self.dict['disc']['release-list'][0]['medium-list'][i]['track-list'][j][
                                                  'length'],
                                              None, self.dict['disc']['release-list'][0]['medium-list'][i]['track-list']
                                              [j]['recording']['artist-credit'][0]['artist']['name']))
        except IndexError:
            for i in range(0, len(self.dict['disc']['release-list'][0]['medium-list'][0]['track-list'])):
                tracks.append(
                    TrackInfo(self.dict['disc']['release-list'][0]['medium-list'][0]['track-list'][i]['recording'][
                                  "title"],
                              self.dict['disc']['release-list'][0]['medium-list'][0]['track-list'][i]['length'],
                              None, None))
        return tracks

    def parse_for_cover(self):
        if self.dict['disc']['release-list'][0]['cover-art-archive']['artwork'] == 'true':
            print(self._mb_id)
            """
            cover_list = musicbrainzngs.get_image_list(self._mb_id)
            for i in range(len(cover_list['images'])):
                if cover_list['images'][i]['comment'].find(self._album) != -1:
                    if cover_list['images'][i]['comment'].find('Front') != -1:
                        cover = musicbrainzngs.get_image(self._mb_id, i)
            """
            cover = musicbrainzngs.get_image(self._mb_id, 'front')
            return cover
        else:
            print('no cover!')
            return ""

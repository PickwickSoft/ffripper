from cd_info_parser import CdInfoParser
from track_info import TrackInfo
from errors import Reason, RipperError
from cdrom_info_object import CDInfo


class CdDiscParser(CdInfoParser):

    def __init__(self, dictionary):
        self.dict = dictionary
        self.disc_id = self.dict['disc']['id']

    def get_disc_info(self):
        try:
            album = self.parse_for_album()
            artist = self.parse_for_artist()
            tracks = self.parse_for_tracks()
        except:
            raise RipperError(Reason.UNKNOWNERROR, "An unknown Error occurred while Parsing")
        return CDInfo(album, artist, tracks)

    def parse_for_album(self):
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
                            print(self.dict['disc']['release-list'][0]['medium-list'][i]['track-list'][i]['recording'][
                                      "title"])
                            for j in range(len(self.dict['disc']['release-list'][0]['medium-list'][i]['track-list'])):
                                tracks.append(
                                    TrackInfo(self.dict['disc']['release-list'][0]['medium-list'][i]['track-list'][j]
                                              ['recording']["title"],
                                              self.dict['disc']['release-list'][0]['medium-list'][i]['track-list'][j][
                                                  'length'],
                                              None, None))
        except IndexError:
            for i in range(0, len(self.dict['disc']['release-list'][0]['medium-list'][0]['track-list'])):
                tracks.append(
                    TrackInfo(self.dict['disc']['release-list'][0]['medium-list'][0]['track-list'][i]['recording'][
                                  "title"],
                              self.dict['disc']['release-list'][0]['medium-list'][0]['track-list'][i]['length'],
                              None, None))
        return tracks

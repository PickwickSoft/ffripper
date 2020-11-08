from cd_info_parser import CdInfoParser
from track_info import TrackInfo
from cdrom_info_object import CDInfo


class CdStubParser(CdInfoParser):

    def __init__(self, dictionary):
        self.dict = dictionary

    def get_disc_info(self):
        album = self.parse_for_album()
        artist = self.parse_for_artist()
        tracks = self.parse_for_tracks()
        return CDInfo(album, artist, tracks)

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
                                    self.dict['cdstub']["track-list"][i]["length"], None, None))
        return tracks

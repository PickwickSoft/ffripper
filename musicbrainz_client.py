#! /usr/bin/env python3

import musicbrainzngs
import discid
from errors import RipperError, Reason


class MusicbrainzClient:

    def __init__(self):
        self.id = None

    def get_disk_id(self):
        try:
            disc = discid.read(discid.get_default_device())
            self.id = disc.id
            print(self.id)
        except discid.DiscError:
            print("Sorry, no device found!")

    def get_metadata(self):
        self.get_disk_id()
        musicbrainzngs.set_useragent("ffRipper", "0.1")
        try:
            result = musicbrainzngs.get_releases_by_discid(self.id, includes=["recordings", "artists", "recording-rels",
                                                                              "labels", "artist-rels", "release-rels",
                                                                              "work-rels", "aliases"])
        except musicbrainzngs.musicbrainz.NetworkError:
            raise RipperError(Reason.NETWORKERROR, "No Internet Connection")
        except:
            # raise RipperError(Reason.MUSICBRAINZERROR, "An Error occurred while receiving Metadata from Musicbrainz")
            result = None
            return result
        if result is None:
            # raise RipperError(Reason.METADATANOTFOUNDERROR, "No Metadata available")
            pass

        return result

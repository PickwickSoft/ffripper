from musicbrainz_client import MusicbrainzClient
from stub_parser import CdStubParser
from disc_parser import CdDiscParser


class Metadata:

    def __init__(self):
        musicbrainz_client = MusicbrainzClient()
        data = musicbrainz_client.get_metadata()
        if data is not None:
            if data.get("cdstub"):
                self.parser = CdStubParser(data)
            elif data.get("disc"):
                self.parser = CdDiscParser(data)
            self.metadata = self.parser.get_disc_info()

    def get_album(self):
        try:
            return self.metadata.get_album()
        except AttributeError:
            return ""

    def get_artist(self):
        try:
            return self.metadata.get_artist()
        except AttributeError:
            return ""

    def get_tracks(self):
        try:
            return self.metadata.get_tracks()
        except AttributeError:
            return None

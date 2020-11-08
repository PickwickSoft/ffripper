class CDInfo:

    def __init__(self, album, artist, tracks):
        self.album = album
        self.artist = artist
        self.tracks = tracks

    def get_album(self):
        return self.album

    def get_artist(self):
        return self.artist

    def get_tracks(self):
        return self.tracks

class TrackInfo:

    def __init__(self, track_name, track_length, track_year, track_artist):
        self.track_name = track_name
        self.track_length = track_length
        self.track_year = track_year
        self.track_artist = track_artist

    def get_name(self):
        return self.track_name

    def get_length(self):
        return self.track_length

    def get_year(self):
        return self.track_year

    def get_artist(self):
        return self.track_artist

from enum import Enum


class RipperError(Exception):

    def __init__(self, reason, text):
        self.reason = reason
        self.text = text


class Reason(Enum):
    UNKNOWNERROR = 0
    NETWORKERROR = 1
    MUSICBRAINZERROR = 2
    METADATANOTFOUNDERROR = 3
    FFMPEGERROR = 4
    NODISCERROR = 5

    def to_string(self):
        if self == Reason.NETWORKERROR:
            return "Network Error"
        elif self == Reason.METADATANOTFOUNDERROR:
            return "Metadata Not Found Error"
        elif self == Reason.MUSICBRAINZERROR:
            return "Musicbrainz Error"
        elif self == Reason.FFMPEGERROR:
            return "FFMPEG Error"
        elif self == Reason.NODISCERROR:
            return "No Disc Found Error"
        else:
            return "Unknown"

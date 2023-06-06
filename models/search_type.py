from enum import Enum


class SearchType(str, Enum):
    album = "album"
    artist = "artist"
    playlist = "playlist"
    track = "track"

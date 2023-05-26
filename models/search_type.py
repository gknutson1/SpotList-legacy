from enum import Enum


class SearchType(str, Enum):
    album = "album"
    artist = "artist"
    playlist = "playlist"
    track = "track"
    show = "show"
    episode = "episode"
    audiobook = "audiobook"

from pydantic import BaseModel, Field

from models.track import Track
from models.spotify_playlist import SpotifyPlaylist
from models.album import Album


class SearchResult(BaseModel):
    tracks: list[Track] | None = Field(description="List of tracks matching the search. `Null` if no results")
    playlists: list[SpotifyPlaylist] | None = Field(description="List of playlists matching the search. `Null` if no results")
    albums: list[Album] | None = Field(description="List of albums matching the search. `Null` if no results")

    @staticmethod
    def from_raw(raw: dict):
        pass
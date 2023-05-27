from pydantic import BaseModel, Field

from models.track import Track
from models.spotify_playlist import SpotifyPlaylist
from models.album import Album
from models.artist import Artist


class SearchResult(BaseModel):
    tracks: list[Track] | None = Field(description="List of tracks matching the search. `Null` if no results.")
    playlists: list[SpotifyPlaylist] | None = Field(description="List of playlists matching the search. `Null` if no results.")
    albums: list[Album] | None = Field(description="List of albums matching the search. `Null` if no results.")
    artists: list[Artist] | None = Field(description="List of artists matching the search. `Null` if no results.")

    @staticmethod
    def from_raw(raw: dict):
        return SearchResult(
                tracks=[Track.from_raw(i) for i in raw.get("tracks").get("items")] if raw.get("tracks") else None,
                playlists=[SpotifyPlaylist.from_raw(i) for i in raw.get("playlists").get("items")] if raw.get("playlists") else None,
                albums=[Album.from_raw(i) for i in raw.get("albums").get("items")] if raw.get("albums") else None,
                artists=[Artist.from_raw(i) for i in raw.get("artists").get("items")] if raw.get("artists") else None
                )
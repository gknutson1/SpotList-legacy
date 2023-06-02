from pydantic import BaseModel, Field

from models.spotify_user import SpotifyUser
from models.track import Track


class PlaylistItem(BaseModel):
    added_at: str | None = Field(description="Date the track was added. May return `null` on old playlists.")
    added_by: SpotifyUser | None = Field(description="User who added the track. May return `null` on old playlists.")
    is_local: bool = Field(description="`true` if the track is a local file instead of a Spotify song.")
    track: Track = Field(description="Information about the track.")

    @staticmethod
    def from_raw(raw: dict):
        return PlaylistItem(
                added_at=raw.get('added_at'),
                added_by=SpotifyUser.from_raw(raw.get('added_by')),
                is_local=raw.get('is_local'),
                track=Track.from_raw(raw.get('track'))
                )

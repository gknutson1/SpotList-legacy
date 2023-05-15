from pydantic import BaseModel, Field

from models.album import Album
from models.spotify_user import SpotifyUser


class Track(BaseModel):
    album: Album = Field(description="The album the track belongs to.")
    artists: list[SpotifyUser] = Field(description="A list of artists credited with working on this track.")
    disc_number: int = Field(description="The disc number (usually 1 unless the album consists of more than one disc).")
    duration: int = Field(description="Length of the track in milliseconds.")
    explicit: bool = Field(description="Whether or not the track has explicit lyrics."
                                       "( true = yes it does; false = no it does not OR unknown).")
    spotify_url: str = Field(title="Spotify URL", description="URL that opens the album in Spotify.")
    spotify_id: str = Field(title="Spotify ID", description="ID that can be used to access the album from the API.")
    name: str = Field(description="Name of the track.")
    popularity: str = Field(
        description="The popularity of the track. The value will be between 0 and 100, "
                    "with 100 being the most popular."
        )
    preview: str | None = Field(description="A link to a 30 second preview of the song in MP3 format. May be `null`.")
    track_number: int = Field(description="The number of the track. If an album has several discs, "
                                          "the track number is the number on the specified disc.")
    is_local: bool = Field(description="`true` if the track is a local file instead of a Spotify song.")

    @staticmethod
    def from_raw(raw: dict):
        return Track(
                album=Album.from_raw(raw.get('album')),
                artists=[SpotifyUser.from_raw(i) for i in raw.get('artists')],
                disc_number=raw.get('disc_number'),
                duration=raw.get('duration_ms'),
                explicit=raw.get('explicit'),
                spotify_url=raw.get('external_urls').get('spotify'),
                spotify_id=raw.get('id'),
                name=raw.get('name'),
                popularity=raw.get('popularity'),
                preview=raw.get('preview_url'),
                track_number=raw.get('track_number'),
                is_local=raw.get('is_local')
                )

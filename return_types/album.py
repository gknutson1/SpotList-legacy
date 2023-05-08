from enum import Enum

from pydantic import BaseModel, Field

from return_types.spotify_user import SpotifyUser


class AlbumType(str, Enum):
    album = "album"
    single = "single"
    compilation = "compilation"


class Album(BaseModel):
    album_type: AlbumType = Field(description="The type of the album - one of 'album', 'single' or 'compilation.")
    total_tracks: int = Field(description="Number of tracks in the album.")
    spotify_url: str = Field(title="Spotify URL", description="URL that opens the album in Spotify.")
    spotify_id: str = Field(title="Spotify ID", description="ID that can be used to access the album from the API.")
    # Broken for some reason
    # images: Optional[list[str]] = Field(description="A list of 0-3 thumbnail images for the album, "
    #                                                 "returned by size in descending order.")
    name: str = Field(description="The name of the album.")
    release_date: str = Field(description="the date the album was released. May be accurate to year, month, or day.")
    genres: list[str] = Field(description="List of genres that the album is associated with. May be empty.")
    popularity: int | None = Field(
        description="The popularity of the album. The value will be between 0 and 100, "
                    "with 100 being the most popular. May be `null` if album is not ranked."
        )
    artists: list[SpotifyUser] = Field(description="A list of artists credited with working on this album.")

    @staticmethod
    def from_raw(raw: dict):
        return Album(
                album_type=AlbumType(raw.get('album_type')),
                total_tracks=raw.get('total_tracks'),
                spotify_url=raw.get('external_urls').get('spotify'),
                spotify_id=raw.get('id'),
                # Broken for some reason
                # images=[i.get('url') for i in raw.get('images')],
                name=raw.get('name'),
                release_date=raw.get('release_date'),
                genres=raw.get('genres', []),
                popularity=raw.get('popularity'),
                artists=[SpotifyUser.from_raw(i) for i in raw.get('artists')]
                )

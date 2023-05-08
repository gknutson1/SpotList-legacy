from pydantic import BaseModel, Field

from return_types.spotify_user import SpotifyUser


class Playlist(BaseModel):
    collaborative: bool = Field(description="`true` if the owner allows other users to modify the playlist.")
    description: str | None = Field(description="The playlist description. Only returned for modified, "
                                                "verified playlists, otherwise `null`.")
    spotify_url: str = Field(title="Spotify URL", description="URL that opens the playlist in Spotify.")
    spotify_id: str = Field(title="Spotify ID", description="ID that can be used to access the playlist from the API.")
    images: list[str] = Field(description="A list of 0-3 thumbnail images for the playlist, "
                                          "returned by size in descending order.")
    name: str = Field(description="The name of the playlist.")
    public: bool | None = Field(description="The playlist's visibility. `true` the playlist is public, `false` if "
                                            "the playlist is private, `null` if the playlist status is not relevant.")
    total_tracks: int = Field(description="Number of tracks in the playlist.")
    owner: SpotifyUser = Field(description="The user who owns the playlist.")

    @staticmethod
    def from_raw(raw: dict):
        return Playlist(
                collaborative=raw.get('collaborative'),
                description=raw.get('description'),
                spotify_url=raw.get('external_urls').get('spotify'),
                spotify_id=raw.get('id'),
                images=[i.get('url') for i in raw.get('images')],
                name=raw.get('name'),
                public=raw.get('public'),
                total_tracks=raw.get('tracks').get('total'),
                owner=SpotifyUser.from_raw(raw.get('owner'))
                )

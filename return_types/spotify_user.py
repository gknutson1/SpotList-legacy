from typing import Optional

from pydantic import BaseModel, Field


class SpotifyUser(BaseModel):
    spotify_url: str = Field(title="Spotify URL", description="URL that opens the user's profile in Spotify.")
    spotify_id: str = Field(title="Spotify ID", description="ID that can be used to access the user from the API.")
    display_name: str | None = Field(description="The profile name of the user, as they would appear in "
                                                 "the Spotify app. May be `null` in certain situations.")

    @staticmethod
    def from_raw(raw: dict):
        return SpotifyUser(
                spotify_url=raw.get('external_urls').get('spotify'),
                spotify_id=raw.get('id'),
                display_name=raw.get('display_name') if raw.get('display_name') else raw.get('name')
                )

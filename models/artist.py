from pydantic import BaseModel, Field


class Artist(BaseModel):
    spotify_url: str = Field(title="Spotify URL", description="URL that opens the artist's profile in Spotify.")
    spotify_id: str = Field(title="Spotify ID", description="ID that can be used to access the artist from the API.")
    name: str | None = Field(description="The profile name of the artist, as they would appear in the Spotify app.")
    followers: int = Field(description="Number of followers that the artist has on Spotify")
    genres: list[str] = Field(description="List of genres the artist is associated with. "
                                          "If not yet classified, the array is empty.")
    popularity: int = Field(description="The popularity of the artist. Between 0 and 100, with 100 being the most "
                                        "popular. Calculated from the popularity of all the artist's tracks.")
    images: list[str] = Field(description="A list of 0-3 thumbnail images for the artist, "
                                          "returned by size in descending order.")

    def __eq__(self, other):
        return isinstance(other, Artist) and self.spotify_id == other.spotify_id

    @staticmethod
    def from_raw(raw: dict):
        return Artist(
                spotify_url=raw.get('external_urls').get('spotify'),
                spotify_id=raw.get('id'),
                name=raw.get('display_name') if raw.get('display_name') else raw.get('name'),
                followers=raw.get("followers").get("total"),
                genres=raw.get("genres"),
                popularity=raw.get("popularity"),
                images=[i.get("url") for i in raw.get("images")])

from pydantic import BaseModel, Field


class Playlist(BaseModel):
    playlist_id: str = Field(description="Unique id of the playlist.")
    name: str = Field(description="Name of the playlist.")
    description: str | None = Field(description="Description of the playlist. May be `Null`.")
    created_at: str = Field(description="Date and time the playlist was created.")
    last_built: str = Field(description="Last time the playlist was built. May be `Null` if it has not been built yet.")
    rule_count: int = Field(description="Number of rules that define the playlist.")
    is_public: bool = Field(description="True if playlist is public, False otherwise.")

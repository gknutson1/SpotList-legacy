from pydantic import BaseModel, Field


class Ruleset(BaseModel):
    created_at: int | None = Field(description="Date the ruleset was created.")
    id: str | None = Field(description="Unique identifier of the ruleset. Matches the Spotify ID of paired playlist.")
    last_built: bool = Field(description="Last time the playlist was built and sent to Spotify.")

    @staticmethod
    def from_raw(raw: dict):
        return None

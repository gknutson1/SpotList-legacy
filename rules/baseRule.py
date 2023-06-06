from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from models.track import Track



class InputType(str, Enum):
    string = "string"
    number = "number"
    artist = "artist"
    album = "album"
    date = "date"


class RuleDescription(BaseModel):
    name: str = Field(description="The name of the rule")
    description: str = Field(description="Describes the effects the rule has on the playlist")
    allow_add: bool = Field(description="If this rule can be used to add new songs to the playlist")
    allow_remove: bool = Field(description="If this rule can be used to remove song from the playlist")
    input_type: InputType = Field(description="What kind of input the rule can accept")
    rule_content: Any | None = Field(description="What value the rule is currently set to")



class BaseRule:

    @staticmethod
    def describe() -> RuleDescription:
        raise NotImplementedError("No description provided for this rule")

    @staticmethod
    def add_tracks(user, tracks: list[Track], data) -> list[Track]:
        raise NotImplementedError("Add method not implemented for this rule")

    @staticmethod
    def remove_tracks(user, tracks: list[Track], data) -> list[Track]:
        raise NotImplementedError("Remove method not implemented for this rule")
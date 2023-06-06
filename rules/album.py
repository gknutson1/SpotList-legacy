from models import Track
from rules.baseRule import BaseRule, RuleDescription, InputType
from user import User


class Album(BaseRule):

    @staticmethod
    def describe() -> RuleDescription:
        return RuleDescription(
                name="by Album",
                description="adds or removes all songs on a specified album",
                allow_add=True,
                allow_remove=True,
                input_type=InputType.album
                )

    @staticmethod
    def add_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

    @staticmethod
    def remove_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

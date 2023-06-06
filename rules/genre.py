from models import Track
from rules.baseRule import BaseRule, RuleDescription, InputType
from user import User


class Genre(BaseRule):

    @staticmethod
    def describe() -> RuleDescription:
        return RuleDescription(
                name="by genre",
                description="removes songs that are considered part of a certain genre",
                allow_add=False,
                allow_remove=True,
                input_type=InputType.string
                )

    @staticmethod
    def add_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

    @staticmethod
    def remove_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

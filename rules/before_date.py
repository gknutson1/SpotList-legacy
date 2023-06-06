from models import Track
from rules.baseRule import BaseRule, RuleDescription, InputType
from user import User


class BeforeDate(BaseRule):

    @staticmethod
    def describe() -> RuleDescription:
        return RuleDescription(
                name="published before",
                description="removes songs published on or before a specified date",
                allow_add=False,
                allow_remove=True,
                input_type=InputType.date
                )

    @staticmethod
    def add_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

    @staticmethod
    def remove_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

from models import Track
from rules.baseRule import BaseRule, RuleDescription, InputType
from user import User


class LessPopular(BaseRule):

    @staticmethod
    def describe() -> RuleDescription:
        return RuleDescription(
                name="less popular than",
                description="removes songs with a lower popularity value (between 1 and 100) than specified",
                allow_add=False,
                allow_remove=True,
                input_type=InputType.number
                )

    @staticmethod
    def add_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

    @staticmethod
    def remove_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        pass

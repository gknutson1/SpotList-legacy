from models import Track
from rules.baseRule import BaseRule, RuleDescription, InputType
from user import User


class AfterDate(BaseRule):

    @staticmethod
    def describe() -> RuleDescription:
        return RuleDescription(
                name="published after",
                description="removes songs published on or after a certain date",
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

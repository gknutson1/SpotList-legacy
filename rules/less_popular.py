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
    def remove_tracks(user: User, tracks: list[Track], data: int) -> list[Track]:
        for i in tracks:
            if i.popularity < data:
                tracks.remove(i)

        return tracks

from datetime import datetime

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
    def remove_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        for i in tracks:
            match i.album.release_date.count("-"):
                case 1:
                    release = datetime.strptime(i.album.release_date, "%Y-%m")
                case 2:
                    release = datetime.strptime(i.album.release_date, "%Y-%m-%d")
                case _:
                    raise Exception("Date format not recognized")

            if release < datetime.strptime(data, "%Y-%m-%d"):
                tracks.remove(i)
        return tracks

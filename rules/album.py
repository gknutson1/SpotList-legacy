import models
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
        album = models.Album.from_raw(user.get(f"/albums/{data}"))

        request = user.get(f"/albums/{data}/tracks", params={"limit": 50})

        while True:
            for i in request["items"]:
                track = models.Track.from_raw(i | album)
                if track not in tracks: tracks.append(track)

            if not request["next"]: break
            request = user.get(request["next"], raw_url=True)

        return tracks


    @staticmethod
    def remove_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        for i in tracks:
            if i.album.spotify_id == data:
                tracks.remove(i)

        return tracks

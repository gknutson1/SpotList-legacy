import models.artist
from models import Track, Album
from rules.baseRule import BaseRule, RuleDescription, InputType
from user import User


class Artist(BaseRule):

    @staticmethod
    def describe() -> RuleDescription:
        return RuleDescription(
                name="by Artist",
                description="Adds or removes tracks based on the artist's credited on the tracks",
                allow_add=True,
                allow_remove=True,
                input_type=InputType.artist
                )

    @staticmethod
    def add_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        albums: list[str] = []
        request = user.get(f"/artists/{data}/albums", {"limit": 50})

        while True:
            albums += (i["id"] for i in request["items"])
            if not request["next"]: break
            request = user.get(request["next"], raw_url=True)

        for offset in range(0, len(albums), 20):
            request = user.get("/albums", {"ids": ",".join(albums[offset:offset+20])})
            for album in request['albums']:
                album_tracks = album['tracks']['items']

                tracks += (Track.from_raw(i | {"album": album}) for i in album_tracks if
                           Track.from_raw(i | {"album": album}) not in tracks)

                if album['tracks']['next']:
                    album_tracks = user.get(album['tracks']["next"], raw_url=True)
                    while True:
                        tracks += (Track.from_raw(i | {"album": album}) for i in album_tracks['items'] if
                                   Track.from_raw(i | {"album": album}) not in tracks)

                        if not album_tracks['next']: break
                        album_tracks = user.get(album['next'], raw_url=True)

        return tracks



    @staticmethod
    def remove_tracks(user: User, tracks: list[Track], data: str) -> list[Track]:
        for i in tracks:

            if data in (artist.spotify_id for artist in i.artists):
                tracks.remove(i)

        return tracks

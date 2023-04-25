from datetime import datetime

import cfg
from rules import BaseRule


class Playlist:
    playlistID: str
    last_built: datetime
    rules: list[BaseRule]

    def __init__(self, playlistID: str, last_built: datetime) -> None:
        self.playlistID = playlistID
        self.last_built = last_built

        rule_data = cfg.db.execute(f"SELECT * FROM rules WHERE playlist = {playlistID} ORDER BY exec_order").fetchall()

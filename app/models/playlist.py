import random
import threading
from enum import Enum
from typing import List

import yt_dlp

from .song import Song


class LoopMode(Enum):
    NONE = 0
    CURRENT = 1
    ALL = 2


class Playlist:
    songs: List[Song]
    paused: bool
    loop: LoopMode
    current_song: int

    def __init__(self) -> None:
        self.songs = []
        self.paused = False
        self.loop = LoopMode.NONE
        self.current_song = 0

    async def get_current_song(self) -> Song | None:
        if self.loop == LoopMode.ALL and self.current_song >= len(self.songs):
            self.restart()
        if self.current_song >= len(self.songs) or len(self.songs) == 0 or self.paused:
            return None
        await self.songs[self.current_song].wait_until_downloaded()
        return self.songs[self.current_song]

    def add(self, url: str) -> None:
        # get all song urls of the playlist url
        ydl_opts = {
            "format": "bestaudio/best",
            "extractaudio": True,
            "audioformat": "webm",
            "outtmpl": "%(id)s",
            "noplaylist": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                video_urls = [
                    video.get("original_url", "") for video in info["entries"]
                ]
            else:
                video_urls = [url]
        self._add(video_urls)
        self.paused = False  # Songs were added, so we can presume the user used the play command, so let's unpause

    def _add(self, video_urls: List[str]) -> None:
        self.songs = self.songs + [Song(url) for url in video_urls if url != ""]

    def clear(self) -> None:
        self.songs = []
        self.restart()

    def remove(self, url: str) -> None:
        self.songs = [song for song in self.songs if song.url != url]

    def shuffle(self) -> None:
        random.shuffle(self.songs)

    def next(self) -> None:
        if self.loop == LoopMode.CURRENT:
            return
        self.current_song += 1

    def skip_to(self, url: str) -> bool:
        try:
            self.current_song = self.songs.index(Song(url))
            return True
        except ValueError:
            return False

    def restart(self) -> None:
        # Start playing from the beggining
        self.current_song = 0

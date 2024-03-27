import os

import yt_dlp

from ..config import CACHE_DIR


class Song:
    id: str
    title: str
    url: str
    file_path: str
    channel_name: str
    channel_url: str
    duration: str
    duration_string: str

    def __init__(self, url: str) -> None:
        self.url = url
        self._download()

    def _download(self) -> None:
        dl = yt_dlp.YoutubeDL(
            {
                "format": "bestaudio/best",
                "outtmpl": "%(id)s",
                "extractaudio": True,
                "audioformat": "webm",
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "default_search": "auto",
            }
        )
        # get meta data
        with dl:
            result = dl.extract_info(self.url, download=False)
            # Does result contain the audio?
            if "entries" in result and len(result["entries"]) > 0:
                result = result["entries"][0]
            self.id = result.get("id")
            self.title = result.get("title")
            self.channel_name = result.get("channel")
            self.channel_url = result.get("uploader_url")
            self.duration = result.get("duration")
            self.duration_string = result.get("duration_string")
        if not os.path.exists("./cache"):
            os.mkdir(CACHE_DIR)
        if not os.path.exists(f"{CACHE_DIR}/{self.id}"):
            dl.download([self.url])
            os.rename(self.id, f"{CACHE_DIR}/{self.id}")
        self.file_path = f"{CACHE_DIR}/{self.id}"

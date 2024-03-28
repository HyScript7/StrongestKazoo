import asyncio
import logging
import os
import threading

import yt_dlp

from ..config import CACHE_DIR

logger = logging.getLogger("strongest.downloader")


class Song:
    id: str
    title: str
    url: str
    file_path: str
    channel_name: str
    channel_url: str
    duration: str
    duration_string: str
    _download_event: asyncio.Event
    _download_thread: threading.Thread

    def __init__(self, url: str) -> None:
        self.url = url
        logger.info("Created Song %s", self.url)
        self._download_event = asyncio.Event()
        self.download()

    def download(self) -> None:
        logger.info("Creating download thread for %s", self.url)
        self._download_thread = threading.Thread(
            target=lambda: asyncio.run(self._download())
        )
        self._download_thread.start()

    async def wait_until_downloaded(self) -> None:
        await self._download_event.wait()

    async def _download(self) -> None:
        logger.info("Downloading %s", self.url)
        dl = yt_dlp.YoutubeDL(
            {
                "format": "bestaudio/best",
                "outtmpl": f"{CACHE_DIR}/%(id)s",
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
            logger.info("Was unable to find %s in cache, downloading!", self.url)
            dl.download([self.url])
        else:
            logger.info("Found %s in cache", self.url)
        self.file_path = f"{CACHE_DIR}/{self.id}"
        self._download_event.set()
        logger.info("Finished downloading %s", self.url)

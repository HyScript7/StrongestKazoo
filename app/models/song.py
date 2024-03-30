import asyncio
import logging
import os
from typing import List

import yt_dlp
from yt_dlp.utils import download_range_func

from ..threaded_executor import ThreadedExecutor, threaded

logger = logging.getLogger("strongest.song")

CACHE_DIR = "./cache"


class Meta:
    url: str
    vid: str
    title: str
    channel_name: str
    channel_url: str
    _fetch_thread: ThreadedExecutor | None

    def __init__(self, url: str) -> None:
        logger.info("Created SongMeta object for %s", url)
        self._fetch_thread = self._fetch_meta(url)

    async def wait_until_fetched(self) -> None:
        """
        Asynchronously waits until the metadata fetch is completed.

        This function waits until the fetch thread has finished fetching the data.
        It uses the `wait()` method of the `fetch_thread` attribute to wait for the completion.

        Returns:
            None: This function does not return anything.
        """
        logger.debug("Someone is waiting for a song object to fetch meta data")
        await self._fetch_thread.wait()

    def get_fragment_dir(self) -> str:
        """
        Return the directory path for where the fragments of this song will be stored
        """
        return f"{CACHE_DIR}/{self.vid}"

    @threaded
    async def _fetch_meta(self, url) -> None:
        logger.info("Started fetching metadata for %s", url)
        ydl_opts = {
            "format": "bestaudio/best",
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "no_playlist": True,
            "no_search": True,
            "verbose": False,
            "simulate": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            self.vid = info["id"]
            self.url = info["webpage_url"]
            self.title = info["title"]
            self.channel_name = info.get("channel", "")
            self.channel_url = info.get("uploader_url") or info.get(
                "channel_url", self.url
            )
            self.duration = info["duration"]
        logger.info("Finished fetching metadata for %s", url)


class Fragment:
    fid: int
    start: int
    end: int
    meta: Meta
    _download_thread: ThreadedExecutor | None

    def __init__(self, meta: Meta, fid: int, start: int, end: int) -> None:
        logger.debug("Created fragment from %d to %d for %s", start, end, meta.url)
        self.meta = meta
        self.fid = fid
        self.start = start
        self.end = end
        self._download_thread = None

    def is_downloaded(self) -> bool:
        """Returns whether the fragment's file is downloaded or not

        Returns:
            bool: True if it is in cache, otherwise False
        """
        return os.path.exists(self.get_fragment_filepath())

    async def wait_until_downloaded(self) -> None:
        """Waits until the fragment's file is downloaded
        Downloads it if it no longer exists or wasn't present in the cache in the first place
        """
        logger.debug(
            "Someone is waiting for a fragment of %s to download", self.meta.url
        )
        self.start_download_thread()  # Doesn't do anything if the download thread is already running
        await self._download_thread.wait()

    def start_download_thread(self):
        """
        Starts a new download thread if one does not already exist.
        Does not re-download if the fragment is already in the cache

        This function checks if a download thread is already running. If a thread is not running,
        or if the current thread has been set but the download has not completed, a new download thread
        is started.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        if self._download_thread is not None:
            if not self._download_thread.is_set():
                return
            if self.is_downloaded():
                return
        logger.debug("Creating download job for a fragment of %s", self.meta.url)
        self._download_thread = self._download()

    def get_fragment_filepath(self) -> str:
        """
        Return the file path for the fragment file
        """
        return f"{self.meta.get_fragment_dir()}/{self.fid}"

    @threaded
    async def _download(self) -> None:
        if self.is_downloaded():
            logger.debug(
                "Fragment %d to %d of %s is cached! Will not re-download.",
                self.start,
                self.end,
                self.meta.url,
            )
            return
        logger.debug(
            "Starting download of fragment %d to %d of %s",
            self.start,
            self.end,
            self.meta.url,
        )
        yt_opts = {
            "format": "bestaudio/best",
            "outtmpl": self.get_fragment_filepath(),
            "extractaudio": True,
            "audioformat": "webm",
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "no_playlist": True,
            "no_search": True,
            "verbose": False,
            "download_ranges": download_range_func(None, [(self.start, self.end)]),
        }

        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download(self.meta.url)
        logger.debug(
            "Finished download of fragment %d to %d of %s",
            self.start,
            self.end,
            self.meta.url,
        )


class Song:
    meta: Meta
    fragments: List[Fragment]
    _setup_task: asyncio.Task

    def __init__(self, url) -> None:
        logger.info("Created new song: %s", url)
        self._setup_task = asyncio.get_event_loop().create_task(self._download(url))

    async def wait_until_ready(self) -> None:
        """Waits until the file's meta data is fetched and fragments are prepared to be downloaded"""
        logger.debug("Someone is waiting for a song to finish initialization")
        await self._setup_task

    async def _download(self, url) -> None:
        logger.debug("Creating Metadata object")
        self.meta = Meta(url)
        await self.meta.wait_until_fetched()
        logger.debug("Metadata object created, creating fragments")
        self._create_fragments()
        logger.debug("Fragments created")

    def _create_fragments(self) -> None:
        duration = int(self.meta.duration)
        start = 0
        fragments = []
        
        FRAGMENT_SIZE: int = 10

        while start < duration:
            end = min(start + FRAGMENT_SIZE, duration)
            if len(fragments) > 0 and end - fragments[-1].end < FRAGMENT_SIZE:
                fragments[-1].end = end
            else:
                fragments.append(Fragment(self.meta, len(fragments), start, end))
            start = end

        self.fragments = fragments


class Playlist:
    url: str
    songs: List[Song]
    urls: List[str]
    _fetch_thread: ThreadedExecutor | None
    _create_task: asyncio.Task

    def __init__(self, url: str) -> None:
        logger.info("Playlist loader initialized for %s", url)
        if "playlist?list=" not in url:
            logger.warn("%s is NOT a playlist", url)
            raise ValueError("Not a playlist URL")
        self.url = url
        self.songs = []
        self.urls = []
        self._create_task = asyncio.create_task(self._fetch_and_create_songs())

    async def _fetch_and_create_songs(self) -> None:
        logger.debug("Playlist initialization task started")
        self._fetch_thread = (
            self._fetch_playlist_urls()
        )  # Running this here should avoid a race condition when calling Playlist.wait_until_ready()
        logger.debug("Waiting for urls to download")
        await self._fetch_thread.wait()
        self.songs = self._urls_to_songs(self.urls)
        logger.debug("Playlist initialization task finished")

    async def wait_until_ready(self) -> None:
        """Waits until all songs in the playlist have been fetched and created in Playlist.songs"""
        logger.debug("Someone is waiting for a playlist to finish initialization")
        await self._create_task

    @threaded
    async def _fetch_playlist_urls(self) -> None:
        logger.info("PlaylistLoader started fetching urls for %s", self.url)
        ydl = yt_dlp.YoutubeDL(
            {
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "no_playlist": True,
                "no_search": True,
                "verbose": False,
            }
        )
        with ydl:
            info = ydl.extract_info(self.url, download=False)
        if info.get("entries", None) is None:
            urls = []
        else:
            urls = [
                video.get("original_url", video.get("webpage_url"))
                for video in info["entries"]
            ]
        self.urls = urls
        logger.info("PlaylistLoader finished fetching urls for %s", self.url)

    def _urls_to_songs(self, urls: List[str]) -> List[Song]:
        return [Song(url) for url in urls]

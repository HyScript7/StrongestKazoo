import asyncio
import json
import logging
import os
import urllib
from typing import Dict

from ..config import CACHE_DIR

logger = logging.getLogger("strongest.cache")


def initialize_cache():
    meta_file = CACHE_DIR + "/meta.json"
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
        except OSError as e:
            return
    if not os.path.exists(meta_file):
        try:
            with open(meta_file, "w") as f:
                json.dump({}, f)
        except OSError as e:
            return


def get_params(url: str) -> Dict:
    return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)


class MetaCache:
    """DEPRECATED - USE ASYNCMETACACHE INSTEAD"""

    _cache: Dict

    def __init__(self) -> None:
        initialize_cache()
        self._cache = dict()
        try:
            self.load()
        except FileNotFoundError:
            self.save()

    def get(self, url: str, default: Dict | None = None) -> Dict | None:
        params = get_params(url)
        vid = params.get("list", params.get("v", [None]))[0]
        if vid is None:
            return default
        return self._cache.get(vid, default)

    def set(self, url: str, data: Dict) -> None:
        params = get_params(url)
        vid = params.get("list", params.get("v", [None]))[0]
        if vid is None:
            return None
        self._cache[vid] = data
        self.save()

    def save(self) -> None:
        with open(f"{CACHE_DIR}/meta.json", "w") as f:
            json.dump(self._cache.copy(), f)

    def load(self) -> None:
        with open(f"{CACHE_DIR}/meta.json", "r") as f:
            self._cache = json.load(f)


class AsyncMetaCache:
    _saving_event: asyncio.Event
    _data: Dict

    def __init__(self) -> None:
        logger.debug("Initializing cache...")
        initialize_cache()
        logger.debug("Loading from file...")
        self.load()
        logger.debug("Creating internal event to avoid race conditions...")
        self._saving_event = asyncio.Event()
        self._saving_event.set()

    def get(self, url: str, default: Dict | None = None) -> Dict | None:
        """Returns video data from cache

        Args:
            url (str): The URL of the video
            default (Dict | None, optional): What to return if we don't have it cached. Defaults to None.

        Returns:
            Dict | None: Either the cached data or default
        """
        params = get_params(url)
        vid = params.get("list", params.get("v", [None]))[0]
        if vid is None:
            return default
        return self._data.get(vid, default)

    async def set(self, url: str, data: Dict) -> None:
        """|CORO| Save data to cache

        Args:
            url (str): The URL of the video
            data (Dict): The data we got from the API
        """
        logger.debug("Adding data to cache for %s...", url)
        await self._saving_event
        logger.debug("No longer blocked, adding %s to cache", url)
        params = get_params(url)
        vid = params.get("list", params.get("v", [None]))[0]
        if vid is None:
            return None
        self._data[vid] = data
        await self.save()

    async def save(self) -> None:
        """|CORO| Dump all to cache file
        """
        logger.debug("Save requested, setting event to False")
        self._saving_event = asyncio.Event()
        with open(f"{CACHE_DIR}/meta.json", "w") as f:
            json.dump(self._data, f)
        logger.debug("Save completed, setting event to True")
        self._saving_event.set()

    def load(self) -> None:
        with open(f"{CACHE_DIR}/meta.json", "r") as f:
            self._data = json.load(f)


meta_cache: AsyncMetaCache = AsyncMetaCache()

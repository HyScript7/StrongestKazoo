import random
from enum import Enum
from typing import List

from .song import Song, Fragment, Playlist as PlaylistLoader


class LoopMode(Enum):
    OFF = 0
    CURRENT = 1
    ALL = 2


class Playlist:
    songs: List[Song]
    loopmode: LoopMode
    current_song: int
    current_fragment: int

    def __init__(self) -> None:
        self.songs = []
        self.loopmode = LoopMode.OFF
        self.current_song = 0
        self.current_fragment = 0

    async def get(self) -> str | None:
        """Returns the path to the fragment or None if there is no song

        Returns:
            str: The path to the fragment to play
            None: There is no song to play
        """
        song_count: int = len(self.songs)
        if song_count == 0:
            return None
        if self.current_song >= song_count:
            return None
        song: Song = self.songs[self.current_song]
        await song.wait_until_ready()
        fragment: Fragment = song.fragments[self.current_fragment]
        await fragment.wait_until_downloaded()  # Makes sure the current fragment is downloaded
        return fragment.get_fragment_filepath()

    async def next(self) -> None:
        if len(self.songs) == 0:
            # There are no songs, don't do anything
            return
        song: Song = self.songs[self.current_song]
        await song.wait_until_ready()  # Make sure the current song's fragments exist
        fragments_last_idx: int = len(song.fragments) - 1
        if self.current_fragment >= fragments_last_idx:
            # We were at the last fragment, next song
            self._next_song()
        else:
            # We are not at the end of the song yet, move onto the next fragment
            self._next_fragment()

    async def _next_fragment(self) -> None:
        song: Song = self.songs[self.current_song]
        self.current_fragment += 1
        # We download the next fragment, if there is one
        self._preload_next_fragment(song, self.current_fragment)

    async def _next_song(self) -> None:
        self.current_fragment = 0
        if self.loopmode == LoopMode.CURRENT:
            return
        song_count = len(self.songs)
        if self.current_song >= song_count:
            # If we are already at the end of the queue (after last song), don't do anything
            return
        self.current_song += 1
        # if our current song index is AFTER the end of the playlist
        if self.current_song >= song_count and self.loopmode == LoopMode.ALL:
            self.current_song = 0
        # If loop mode is off, we just move onto the non-existent song.
        # Get current song will handle returning None if we are at the end of the playlist
        # Load the first fragment
        self._preload_next_song()  # Preload the next song if there is one

    def _preload_next_fragment(self, song: Song, current_fragment: int) -> None:
        fragments_last_idx: int = len(song.fragments) - 1
        if current_fragment >= fragments_last_idx:
            return
        song.fragments[
            current_fragment + 1
        ].start_download_thread()  # This won't do anything if it's already downloaded or already in the process of downloading

    def _preload_next_song(self) -> None:
        song_count = len(self.songs)
        # If there is another song after this one, preload it's first fragment
        if self.current_song + 1 < song_count:
            # If the next song exists
            song = self.songs[self.current_song + 1]
            self._preload_next_fragment(
                song, -1
            )  # We are not using the current_fragment to access the current fragment in this function, so this is fine

    async def add(self, url: str) -> None:
        try:
            playlist: PlaylistLoader = PlaylistLoader(url)
            playlist.wait_until_ready()
            self.songs = self.songs + playlist.songs
        except ValueError:
            self.songs.append(Song(url))

    async def remove(self, identifier: int | Song | str) -> None:
        if isinstance(identifier, int):
            if identifier < len(self.songs) and identifier >= 0:
                self.songs.pop(identifier)
        elif isinstance(identifier, Song):
            self.songs.remove(identifier)
        else:
            self.songs = [song for song in self.songs if song.meta.url != identifier]

    def clear(self) -> None:
        self.songs.clear()

    def get_loop_mode(self) -> LoopMode:
        return self.loopmode.name()

    def set_loop_mode(self, loop_mode: LoopMode) -> None:
        self.loopmode = loop_mode

    def cycle_loop_mode(self) -> LoopMode:
        if self.loopmode == LoopMode.OFF:
            self.loopmode = LoopMode.CURRENT
        elif self.loopmode == LoopMode.CURRENT:
            self.loopmode = LoopMode.ALL
        else:
            self.loopmode = LoopMode.OFF
        return self.get_loop_mode()

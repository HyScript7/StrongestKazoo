import asyncio
from typing import Optional

from discord import FFmpegPCMAudio, Guild, VoiceChannel, VoiceClient
from discord.ext import commands

from ..models.playlist import Playlist
from ..models.song import Song


class AudioController:
    playlist: Playlist
    current_song: Optional[Song]
    guild: Guild
    vc: VoiceChannel
    vp: Optional[VoiceClient]
    _playing_event: asyncio.Event
    _playing_task: asyncio.Task

    def __init__(
        self, bot: commands.Bot, vc: VoiceChannel, guild: Optional[Guild] = None
    ) -> None:
        self.playlist = Playlist()
        self.current_song = None
        self.vc = vc
        self.guild = guild if guild else vc.guild
        self.vp = None
        self._playing_event = None

    async def join(self) -> None:
        await self.leave()
        self.vp = await self.vc.connect()

    async def leave(self) -> None:
        if self.vp != None:
            await self.vp.disconnect()
            self.playlist.clear()
            self.current_song = None
            self._playing_event.set()

    async def play(self) -> None:
        self.current_song = await self.playlist.get_current_song()
        self._playing_event = asyncio.Event()
        while self.current_song is not None:
            self.current_song = await self.playlist.get_current_song()
            if (self.current_song is None):
                break
            self.vp.play(FFmpegPCMAudio(self.current_song.file_path), after=self._next)
            await self.wait_until_playing()
            print("Finished playing")
            self._playing_event = asyncio.Event()
        print("Ran out of songs!")
        self.vp.stop()
        
    async def wait_until_playing(self) -> None:
        await self._playing_event.wait()

    def _next(self, error: Optional[Exception] = None) -> None:
        self.playlist.next()
        if self.vp.is_playing:
            self.vp.stop()
        self._playing_event.set()

    def next(self) -> None:
        if self.vp.is_playing:
            self.vp.stop()

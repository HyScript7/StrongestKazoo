from typing import Optional

from discord import Guild, VoiceChannel, VoiceClient, FFmpegPCMAudio
from discord.ext import commands

from ..models.playlist import Playlist
from ..models.song import Song


class AudioController:
    playlist: Playlist
    current_song: Optional[Song]
    guild: Guild
    vc: VoiceChannel
    vp: Optional[VoiceClient]

    def __init__(
        self, bot: commands.Bot, vc: VoiceChannel, guild: Optional[Guild] = None
    ) -> None:
        self.playlist = Playlist()
        self.current_song = None
        self.vc = vc
        self.guild = guild if guild else vc.guild
        self.vp = None

    async def join(self) -> None:
        await self.leave()
        self.vp = await self.vc.connect()

    async def leave(self) -> None:
        if self.vp != None:
            await self.vp.disconnect()
            self.playlist.clear()
            self.current_song = None

    def play(self) -> None:
        self.current_song = self.playlist.get_current_song()
        if self.current_song is None:
            self.vp.stop()
            return
        self.vp.play(FFmpegPCMAudio(self.current_song.file_path), after=self.next)

    def next(self, error: Optional[Exception] = None) -> None:
        self.playlist.next()
        if self.vp.is_playing:
            self.vp.stop()
        self.play()

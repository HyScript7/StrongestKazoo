import asyncio

import discord
from discord import FFmpegPCMAudio, Guild, VoiceChannel, VoiceClient
from discord.ext import commands

from ..models.playlist import Playlist
from ..models.song import Song


class AudioController:
    playlist: Playlist
    current_song: Song | None
    guild: Guild
    vc: VoiceChannel
    vp: VoiceClient | None
    _playing_event: asyncio.Event
    _playing_task: asyncio.Task
    _callback_channel: discord.TextChannel

    def __init__(
        self, bot: commands.Bot, vc: VoiceChannel, guild: Guild | None = None
    ) -> None:
        self.playlist = Playlist()
        self.current_song = None
        self.vc = vc
        self.guild = guild if guild else vc.guild
        self.vp = None
        self._playing_event = None
        self._playing_task = None
        self._callback_channel = None

    async def join(self) -> None:
        await self.leave()
        self.vp = await self.vc.connect()

    async def leave(self) -> None:
        if self.vp != None:
            await self.vp.disconnect()
            self.vp = None
            self.playlist.clear()
            self.current_song = None
            self._playing_event.set()
            if self._playing_task:
                self._playing_task.cancel()

    async def play(self, channel: discord.TextChannel | None = None) -> None:
        self._callback_channel = channel
        self._playing_task = asyncio.create_task(self._play())

    async def announce_current_song(self, song: Song | None) -> None:
        if self._callback_channel is None:
            return
        try:
            # TODO: Use an embed
            if song is None:
                await self._callback_channel.send("No more songs are present in the queue!")
            # TODO: Use an embed
            await self._callback_channel.send(
                f"Now playing: [{song.title}](<{song.url}>) uploaded by [{song.channel_name}](<{song.channel_url}>)"
            )
        except:
            print(f"Detaching callback channel for {self.guild.id}")
            self._callback_channel = None

    async def _play(self) -> None:
        self.current_song = await self.playlist.get_current_song()
        self._playing_event = asyncio.Event()
        while self.current_song is not None:
            await self.announce_current_song(self.current_song)
            if self.current_song is None:
                break
            self.vp.play(FFmpegPCMAudio(self.current_song.file_path), after=self._next)
            await self.wait_until_song_ends()
            self.current_song = await self.playlist.get_current_song()
            self._playing_event = asyncio.Event()
        await self.announce_current_song(self.current_song)
        self.vp.stop()

    async def wait_until_song_ends(self) -> None:
        await self._playing_event.wait()

    def _next(self, error: Exception | None = None) -> None:
        self.playlist.next()
        if self.vp.is_playing:
            self.vp.stop()
        self._playing_event.set()

    def next(self) -> None:
        if self.vp.is_playing:
            self.vp.stop()

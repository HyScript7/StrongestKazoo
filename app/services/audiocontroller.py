import asyncio
from typing import List, Tuple

import discord
from discord.ext import commands

from ..models.playlist import Playlist
from ..models.song import Fragment, Song


async def send_message(channel: discord.TextChannel, *args, **kwargs) -> None:
    """Attempts to send a message in the specified channel
    Doesn't do anything if it fails because of a discord error

    Same as channel.send, but the channel has to be the first argument
    """
    try:
        await channel.send(*args, **kwargs)
    except discord.errors.DiscordException:
        return


class AudioController:
    bot: commands.Bot
    guild: discord.Guild
    _vc: discord.VoiceClient | None
    _callback_channel: discord.TextChannel
    _playlist: Playlist
    _finished_playing: asyncio.Event | None
    _play_task: asyncio.Task | None
    __loop: asyncio.AbstractEventLoop

    def __init__(self, bot: commands.Bot, guild: discord.Guild) -> None:
        self.bot = bot
        self.guild = guild
        self._playlist = Playlist()
        self._finished_playing = None
        self._play_task = None
        self.__loop = asyncio.get_running_loop()
    
    def is_connected(self) -> bool:
        return self._vc is not None

    async def join(
        self, channel: discord.VoiceChannel, callback_channel: discord.TextChannel
    ) -> None:
        if self._vc is not None:
            await send_message(callback_channel, "Already in a voice channel!")
            return
        self._vc = await channel.connect()
        self._callback_channel = callback_channel
        await send_message(self._callback_channel, "Joined the voice channel!")

    async def leave(self) -> None:
        await send_message(self.__callback_channel, "Leaving voice channel!")
        await self._vc.disconnect()
        self._vc = None
        self._callback_channel = None
        self._playlist.clear()

    async def queue(self, url: str) -> None:
        try:
            await self._playlist.add(url)
            await send_message(
                self.__callback_channel, f"Added <{url}> to the playlist!"
            )
        except Exception as e:
            await send_message(self.__callback_channel, "Something went wrong!")
            raise e  # TODO: Delete this in production, as it's only here to help find exceptions

    def queued(self) -> Tuple[List[str], str]:
        """Returns a partitioned list of messages describing the current queue

        Returns:
            List[str]: A partitioned list of strings
        """
        queued = [
            f"[{song.meta.title}]({song.meta.url}) uploaded by [{song.meta.channel_name}]({song.meta.channel_url})"
            for song in self._playlist.songs
            if song._setup_task.done()
        ]
        remaining = f"{len(self._playlist.songs) - len(queued)} more songs, which are still being fetched."
        partitioned = []
        partition = ""
        for i in queued:
            line = f"{partition}\n{i}"
            if len(line) > 2000 - (remaining + 2):
                partitioned.append(partition)
                partition = i
            else:
                partition = line
        partitioned.append(partition)
        return partitioned, remaining

    async def skip(self, quiet: bool = False) -> None:
        """Skips the current song
        Returns:
            None
        """
        await self._vc.stop()
        if not quiet:
            await send_message(self._callback_channel, "Skipped the current song")

    async def play(self) -> None:
        """
        Initialities the audio player task

        This method checks if a play task is already running.
        If not, it creates a new event object to track when the audio playback has finished.
        It then sets the event to indicate that the audio has finished playing.
        Finally, it creates a new play task using the `_play` method and assigns it to the `_play_task` attribute.

        Returns:
            None
        """
        if self._play_task is None:
            self._finished_playing = asyncio.Event()
            self._finished_playing.set()
            # TODO? Perhaps use a seperate thread for the play loop it self (asyncio "executor" param)
            self._play_task = asyncio.create_task(self._play())

    async def stop(self) -> None:
        """Stops the audio player
        Returns:
            None
        """
        if self._play_task is None:
            if self._vp is not None:
                await self.leave()
            return
        await send_message(self._callback_channel, "Stopped playing")
        await self._cleanup()
        await self.leave()

    async def _play(self) -> None:
        """Asynchronously plays audio from the playlist.
        It continuously retrieves fragments from the playlist and plays them using the voice client.
        It sets up an event to signal when the audio playback is finished.
        If there are no more songs in the playlist, it sends a message to the callback channel and then performs cleanup before returning.
        """
        while 1:
            self._finished_playing = asyncio.Event()
            frag: Fragment = await self._playlist.get()
            await self._announce_current_song()
            if frag is None:
                try:
                    return
                finally:
                    await self._cleanup()
            # TODO: Maybe we can use PCMAudio to read from a buffer instead of a file?
            self._vc.play(
                discord.FFmpegPCMAudio(frag.get_fragment_filepath()),
                after=lambda _: asyncio.run_coroutine_threadsafe(
                    self._next(), self.__loop
                ).result(),
            )
            await self._finished_playing.wait()

    async def _next(self) -> None:
        """Asynchronously moves the current song to the next item in the playlist and unblocks the audio playback process. (Blocked event-wise)

        This method checks if the current play task has been cancelled. If it has, the method returns immediately as to not interfiere with cleanup.
        Otherwise, it proceeds to the next item in the playlist and starts playing it.
        After that, it sets an event to indicate that the playback has finished.

        Returns:
            None
        """

        if self._play_task.cancelled():
            return
        await self._playlist.next()
        await self._play()
        self._finished_playing.set()

    async def _cleanup(self) -> None:
        """
        Asynchronous function to perform cleanup tasks. No parameters. Returns None.
        Makes sure the audio player is stopped and then resets to default state.
        """
        self._play_task.cancel()
        if self._vc.is_playing():
            self._vc.stop()
        self._finished_playing.set()
        self._play_task = None

    async def _announce_current_song(self) -> None:
        song = await self._playlist.get()
        if song is None:
            await send_message(
                self.__callback_channel, "No more songs in the playlist!"
            )
        else:
            await send_message(
                self.__callback_channel,
                f"Now playing: {song.meta.title} uploaded by {song.meta.channel_name}",
            )

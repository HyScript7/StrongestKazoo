from typing import Dict
import asyncio

import discord
from discord.ext import commands

from app.models.song import Song
from app.models.playlist import LoopMode, Playlist
from app.services.audiocontroller import AudioController


class Default(commands.Cog):
    bot: commands.Bot
    controllers: Dict[int, AudioController]

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.controllers = dict()

    def _get_controller(self, guild: discord.Guild, voice: discord.VoiceChannel):
        c = self.controllers.get(guild.id, None)
        if c is None:
            self.controllers[guild.id] = AudioController(self.bot, voice, guild)
        return self.controllers[guild.id]

    @commands.hybrid_command(
        name="play",
        usage="&play <url>",
        description="Adds a song or playlist of songs to the queue",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def _play(self, ctx: commands.Context, url: str):
        await ctx.defer()
        vc: discord.VoiceChannel = ctx.author.voice.channel
        if vc is None:
            # TODO: Use an embed
            await ctx.reply("You must be in a voice channel!")
        controller: AudioController = self._get_controller(ctx.guild, vc)
        controller.playlist.add(url)
        if controller.current_song is None:
            if controller.vp is None:
                await controller.join()
            await controller.play(ctx.channel)
            # TODO: Use an embed
            await ctx.reply(f"Started playing <{url}>")
        else:
            # TODO: Use an embed and make sure we filter it to youtube-only before embedding the url
            await ctx.reply(f"Added <{url}> to the playlist!")

    @commands.hybrid_command(
        name="skip",
        usage="&skip",
        description="Skips the current song",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _skip(self, ctx: commands.Context):
        vc: discord.VoiceChannel = ctx.author.voice.channel
        if vc is None:
            # TODO: Use an embed
            await ctx.reply("You must be in a voice channel!")
        controller: AudioController = self._get_controller(ctx.guild, vc)
        controller.next()
        await ctx.reply("Skipped")

    def get_download_status(self, controller: AudioController, song: Song, short: bool = False) -> str:
        emoji_red = "<:Red:931911327700643861>"
        emoji_yellow = "<:Yellow:931911327230877758>"
        emoji_green = "<:Green:931911327675478026>"
        downloaded = song._download_event.is_set()
        if controller.current_song == song:
            if downloaded:
                prepend = emoji_green + " Playing"
            else:
                prepend = emoji_yellow + " Downloading"
        else:
            if downloaded:
                prepend = emoji_yellow + " Downloaded"
            else:
                prepend = emoji_red + " Downloading..."
        if short:
            prepend = f'{prepend.split(">")[0]}>'
        if downloaded:
            return f"{prepend} [{song.title}](<{song.url}>) uploaded by [{song.channel_name}](<{song.channel_url}>) *{song.duration_string}*"
        else:
            try:
                return f"{prepend} [{song.title}](<{song.url}>) uploaded by [{song.channel_name}](<{song.channel_url}>)"
            except:
                return f"{prepend} Loading..."

    @commands.hybrid_command(
        name="queue", usage="&queue", description="Shows the current song queue"
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _queue(self, ctx: commands.Context):
        vc: discord.VoiceChannel = ctx.author.voice.channel
        if vc is None:
            # TODO: Use an embed
            await ctx.reply("You must be in a voice channel!")
        controller: AudioController = self._get_controller(ctx.guild, vc)
        # TODO: Use an embed
        queued_songs_msg = "Queue:\n" + "\n".join(
            [
                self.get_download_status(controller, song)
                for song in controller.playlist.songs[
                    controller.playlist.current_song :
                ]
            ]
        )
        queued_songs_msg = (
            queued_songs_msg
            + "\nHistory:\n"
            + "\n".join(
                [
                    self.get_download_status(controller, song, True)
                    for song in controller.playlist.songs[
                        : controller.playlist.current_song
                    ][::-1]
                ]
            )
        )
        await ctx.reply(queued_songs_msg)

    @commands.hybrid_command(
        name="loop",
        usage="&loop [all/current/off]",
        description="Toggles the loop mode",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _loop(self, ctx: commands.Context, mode: str = None):
        vc: discord.VoiceChannel = ctx.author.voice.channel
        if vc is None:
            # TODO: Use an embed
            await ctx.reply("You must be in a voice channel!")
        controller: AudioController = self._get_controller(ctx.guild, vc)
        emoji_repeat_all = "🔁"
        emoji_repeat_current = "🔂"
        if mode is not None:
            mode = mode.lower()
            if mode.startswith("a"):
                controller.playlist.set_loop_mode(LoopMode.ALL)
                emoji = emoji_repeat_all
            elif mode.startswith("c"):
                controller.playlist.set_loop_mode(LoopMode.CURRENT)
                emoji = emoji_repeat_current
            elif mode.startswith("n") or mode.startswith("o"):
                controller.playlist.set_loop_mode(LoopMode.OFF)
                emoji = ""
            else:
                # TODO: Use an embed
                await ctx.reply("Invalid loop mode, choose one of all/current/off")
                return
        else:
            controller.playlist.next_loop_mode()
            if controller.playlist.loop == LoopMode.ALL:
                emoji = emoji_repeat_all
            elif controller.playlist.loop == LoopMode.CURRENT:
                emoji = emoji_repeat_current
            else:
                emoji = ""
        # TODO: Use an embed
        await ctx.reply(
            f"Repeat {emoji + (' ' if emoji else '')}{controller.playlist.get_loop_mode().name.title()}"
        )


    @commands.hybrid_command(
        name="pause",
        usage="&pause",
        description="Pauses the player",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _pause(self, ctx: commands.Context):
        vc: discord.VoiceChannel = ctx.author.voice.channel
        if vc is None:
            # TODO: Use an embed
            await ctx.reply("You must be in a voice channel!")
        controller: AudioController = self._get_controller(ctx.guild, vc)
        if controller.vp.is_paused():
            # TODO: Use an embed
            await ctx.reply("Already paused!")
        else:
            controller.vp.pause()
            # TODO: Use an embed
            await ctx.reply("You have paused the audio player!")
            

    @commands.hybrid_command(
        name="resume",
        usage="&resume",
        description="Resumes the player if paused",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _pause(self, ctx: commands.Context):
        vc: discord.VoiceChannel = ctx.author.voice.channel
        if vc is None:
            # TODO: Use an embed
            await ctx.reply("You must be in a voice channel!")
        controller: AudioController = self._get_controller(ctx.guild, vc)
        if controller.vp.is_paused():
            controller.vp.resume()
            # TODO: Use an embed
            await ctx.reply("You have unpaused the audio player!")
        else:
            # TODO: Use an embed
            await ctx.reply("Already unpaused!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Default(bot))

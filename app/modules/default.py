from typing import Dict

import discord
from discord.ext import commands

from app.services.audiocontroller import AudioController
from app.models.playlist import LoopMode
from app.embed_factory import create_embed


class Default(commands.Cog):
    bot: commands.Bot
    controllers: Dict[int, AudioController]

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.controllers = dict()

    def _get_controller(self, guild: discord.Guild):
        c = self.controllers.get(guild.id, None)
        if c is None:
            self.controllers[guild.id] = AudioController(self.bot, guild)
        return self.controllers[guild.id]

    @commands.hybrid_command(
        name="join",
        usage="&join [channel]",
        description="Makes the bot join a channel, by default your current channel",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _join(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        controller: AudioController = self._get_controller(ctx.guild)
        if (channel or ctx.author.voice.channel) is None:
            await ctx.reply(embed=create_embed("Error", "You must either run this command in a voice channel or specify one"))
            return
        if not controller.is_connected():
            await controller.join(channel or ctx.author.voice.channel, ctx.channel)
            await ctx.reply(embed=create_embed("Bot Connected", f"Joined <#{(channel or ctx.author.voice.channel).id}>"))
        else:
            if controller._vc.channel == (channel or ctx.author.voice.channel):
                await ctx.reply(embed=create_embed("Bot Already Connected", f"Already connected to <#{(channel or ctx.author.voice.channel).id}>"))
                return
            await controller.leave()
            await controller.join(channel or ctx.author.voice.channel, ctx.channel)
            await ctx.reply(embed=create_embed("Bot Re-Connected", f"Left the previous channel and joined <#{(channel or ctx.author.voice.channel).id}>"))

    @commands.hybrid_command(
        name="leave",
        usage="&leave",
        aliases=["stop"],
        description="Makes the bot leave it's current channel",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _leave(self, ctx: commands.Context):
        controller: AudioController = self._get_controller(ctx.guild)
        if controller.is_connected():
            await controller.stop()
            await ctx.reply(embed=create_embed("Bot Disconnected", "Stopped playing & left the voice channel"))
        else:
            await ctx.reply(embed=create_embed("Error", "The bot is not currently in a channel!"))

    @commands.hybrid_command(
        name="play",
        usage="&play <url>",
        description="Adds the song or playlist to the queue",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _play(self, ctx: commands.Context, url: str):
        await ctx.defer()
        controller: AudioController = self._get_controller(ctx.guild)
        if not controller.is_connected():
            await controller.join(ctx.author.voice.channel, ctx.channel)
        if "list=" in url:
            await ctx.reply(embed=create_embed("Queuing Playlist", f"It appears you are queuing a playlist\nThe bot may take a while to load it, please be patient"))
        await controller.queue(url)
        await ctx.reply(embed=create_embed("Queued", f"Added {url} to the queue!\nTo view the current queue, use `/queue`"))
        await controller.play()

    @commands.hybrid_command(
        name="pause",
        usage="&pause",
        description="Pauses the audio player",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _pause(self, ctx: commands.Context):
        controller: AudioController = self._get_controller(ctx.guild)
        if not controller.is_connected() or controller._vc.is_paused():
            await ctx.reply(embed=create_embed("Error", "The bot is not playing right now!"))
        controller._vc.pause()
        await ctx.reply(embed=create_embed("Paused", "The audio player has been paused.\nUse `/resume` to continue playing."))

    @commands.hybrid_command(
        name="resume",
        usage="&resume",
        aliases=["unpause"],
        description="Pauses the audio player",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _resume(self, ctx: commands.Context):
        controller: AudioController = self._get_controller(ctx.guild)
        if not controller.is_connected():
            await ctx.reply(embed=create_embed("Error", "The bot is currently not in a voice channel!"))
            return
        if controller._vc.is_paused():
            controller._vc.resume()
            await ctx.reply(embed=create_embed("Resumed", "The audio player has been unpaused."))
        else:
            await ctx.reply(embed=create_embed("Error", "The audio player is not paused."))

    @commands.hybrid_command(
        name="skip",
        usage="&skip [number]",
        description="Skips any number of songs (by default 1)",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _skip(self, ctx: commands.Context, num: int = 1):
        await ctx.defer()
        controller: AudioController = self._get_controller(ctx.guild)
        if not controller.is_connected():
            await ctx.reply(embed=create_embed("Error", "The bot is currently not in a voice channel!"))
            return
        if not controller._vc.is_playing():
            await ctx.reply(embed=create_embed("Error", "The audio player is not playing."))
            return
        if num <= 0 or num > 100:
            await ctx.reply(embed=create_embed("Error", "The number of songs to skip must be between 1 and 100 (inclusive)"))
            return
        if num == 1:
            await controller.skip(quiet=True)
        else:
            for _ in range(num - 1):
                controller._playlist.skip()
            await controller.skip(quiet=True)
        await ctx.reply(embed=create_embed("Fast-forward", f"Skipped {num} song{'s' if num > 1 else ''}"))

    @commands.hybrid_command(
        name="queue",
        usage="&queue [page]",
        description="Shows a specific page of the current queue",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _queue(self, ctx: commands.Context, page: int = 1):
        controller: AudioController = self._get_controller(ctx.guild)
        queue, remaining = controller.get_queue("{}", character_limit_per_page=1700) # Leaves us with 300 characters to work with per page
        if len(queue) == 0:
            await ctx.reply(embed=create_embed("Error", "There are no songs in the queue"))
            return
        if page < 1 or page > len(queue):
            await ctx.reply(embed=create_embed("Error", f"Page out of range\nThere {'are' if len(queue) > 1 else 'is'} only {len(queue)} page{'s' if len(queue) > 1 else ''} in the queue!\nThe first page is always `1`."))
            return
        body = f"{'\n'.join(queue[page-1])}\nand {remaining} songs, which are still fetching"
        e = create_embed("Queue", body)
        e.set_footer(f"Page {page}/{len(queue)}")
        await ctx.reply(embed=e)

    @commands.hybrid_command(
        name="loop",
        usage="&loop [all/current/(off/none)]",
        description="Toggles loop mode",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _loop(self, ctx: commands.Context, mode: str = None):
        controller: AudioController = self._get_controller(ctx.guild)
        if mode is None:
            loop_mode = controller._playlist.cycle_loop_mode()
        else:
            mode = mode.lower()
            if mode.startswith("a"):
                controller._playlist.set_loop_mode(LoopMode.ALL)
            elif mode.startswith("c") or mode.startswith("s"):
                controller._playlist.set_loop_mode(LoopMode.CURRENT)
            else:
                controller._playlist.set_loop_mode(LoopMode.NONE)
            loop_mode = controller._playlist.get_loop_mode()
        await ctx.reply(embed=create_embed("Loop", f"Loop mode has been set to `{loop_mode}`"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Default(bot))

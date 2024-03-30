from typing import Dict

import discord
from discord.ext import commands

from app.services.audiocontroller import AudioController


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
        if not controller.is_connected():
            await controller.join(channel or ctx.author.voice.channel, ctx.channel)
        else:
            await controller.leave()
            await controller.join(channel or ctx.author.voice.channel, ctx.channel)

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
        else:
            await ctx.send("The bot is not in a voice channel!")

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
            await ctx.send(
                "It looks like you are queuing a playlist.\n# The bot may be unreposnsive for a while\nDo not panic, you should see your songs in the queue soon."
            )
        await controller.queue(url)
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
        if not controller.is_connected() or controller._vp.is_paused():
            await ctx.send("The bot is not currently playing!")
        controller._vp.pause()
        await ctx.send("The bot has been paused")

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
            await ctx.send("The bot is currently not in a voice channel!")
        if controller._vp.is_paused():
            controller._vp.resume()
            await ctx.send("The bot has been unpaused")
        else:
            await ctx.send("The bot is not paused!")

    @commands.hybrid_command(
        name="skip",
        usage="&skip [number]",
        description="Skips any number of songs (by default 1)",
    )
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def _skip(self, ctx: commands.Context, num: int):
        await ctx.defer()
        controller: AudioController = self._get_controller(ctx.guild)
        if not controller.is_connected():
            await ctx.send("The bot is currently not in a voice channel!")
            return
        if not controller._vc.is_playing():
            await ctx.send("The bot is currently not playing!")
            return
        if num <= 0 or num > 100:
            await ctx.send("The number of songs to skip must be between 1 and 100!")
            return
        if num == 1:
            await controller.skip(quiet=True)
        else:
            for _ in range(num - 1):
                controller._playlist.skip()
            await controller.skip(quiet=True)
        await ctx.send(f"Skipped {num} song{'s' if num > 1 else ''}!")

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
        queue, remaining = controller.queued()
        if len(queue) == 0:
            await ctx.send("The queue is empty")
            return
        if page < 1 or page > len(queue):
            await ctx.send(f"That page does not exist! (There are {len(queue)} pages)")
            return
        await ctx.send(f"{queue[page-1]}\n{remaining}")
        await ctx.reply(f"There are {len(queue)} pages avabiable")


async def setup(bot: commands.Bot):
    await bot.add_cog(Default(bot))

from typing import Dict
import asyncio

import discord
from discord.ext import commands

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
            asyncio.create_task(controller.play())
        await ctx.reply("Started playing")

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Default(bot))

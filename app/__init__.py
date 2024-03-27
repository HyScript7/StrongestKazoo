import asyncio
import glob
import logging
import os
from typing import List

import discord
from discord.ext import commands

from .loggers import configure_logger

configure_logger(
    [
        "strongest",
        "discord",
        "discord.http",
    ]
)

logger = logging.getLogger("strongest.bootstrap")

from .config import PREFIX  # noqa

bot = commands.Bot(PREFIX, intents=discord.Intents.all())


modules_dir = os.path.join(os.path.dirname(__file__), "modules")
extensions = [
    f.replace(os.path.join(modules_dir, ""), "").replace(".py", "")
    for f in glob.glob(os.path.join(modules_dir, "*.py"))
    if not os.path.basename(f).startswith("__")
]

logger.info("Discovered modules: %s", ", ".join(extensions))


async def load_extensions(extensions: List[str]):
    for extension in extensions:
        try:
            await bot.load_extension(f"{__package__}.modules.{extension}")
            logger.info(f"Loaded module {extension}.")
        except Exception as e:
            logger.error(f"Failed to load module {extension}.", exc_info=e)


asyncio.run(load_extensions(extensions))


@bot.event
async def on_ready():
    logger = logging.getLogger("strongest.bot")
    logger.info("Running on discord.py %s", discord.__version__)
    await bot.wait_until_ready()
    await bot.tree.sync()
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name=f"kazoo screeching"
        )
    )

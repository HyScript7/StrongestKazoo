import logging

from decouple import config

logger = logging.getLogger("strongest.config")

TOKEN: str = config("BOT_TOKEN", None)
if TOKEN is None:
    logger.critical("BOT_TOKEN not found in .env file")
    raise Exception("BOT_TOKEN not found in .env file")

PREFIX: str = config("BOT_PREFIX", None)
if PREFIX is None:
    PREFIX = "&"
    logger.warn("BOT_PREFIX not found in .env file, using default: '&'")


CACHE_DIR: str = config("BOT_CACHE_DIR", None)
if CACHE_DIR is None:
    CACHE_DIR = "./cache"
    logger.warn("BOT_CACHE_DIR not found in .env file, using default: './cache'")

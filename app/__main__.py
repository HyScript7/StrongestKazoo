import logging

from discord.errors import LoginFailure

logger = logging.getLogger("strongest.init")
if __name__ == "__main__":
    from . import bot
    from .config import TOKEN

    logger.info("Running bot...")
    # Note that we are not catching unhandled exceptions here, because it will be better to catch them at the point of origin rather than just dropping a wildcard here
    # Additionally, if we catch something here, it's already too late, because that means the bot has crashed.
    try:
        bot.run(TOKEN, log_handler=None)
    except LoginFailure as e:
        logger.critical("Login failed", exc_info=e)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, the bot will stop")
    finally:
        logger.info("Bot stopped")

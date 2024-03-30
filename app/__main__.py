import errno
import time
import logging
import os
import shutil

from discord.errors import LoginFailure

from .config import CACHE_DIR

logger = logging.getLogger("strongest.init")


def create_cache_dir():
    logger.info("Will create cache directory.")
    try:
        os.makedirs(CACHE_DIR)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def delete_cache_dir():
    if os.path.exists(CACHE_DIR):
        logger.info(
            "Will clear cache directory. Press Ctrl+C within 3 seconds to abort!"
        )
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            logger.info("Aborting clear...")
            return
        try:
            shutil.rmtree(CACHE_DIR)
        except OSError as e:
            if e.errno == errno.ENOTEMPTY:
                # Directory is not empty, let's delete it recursively
                for root, dirs, files in os.walk(CACHE_DIR, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(CACHE_DIR)
            else:
                raise


if os.path.exists(CACHE_DIR):
    threshold_size = 16 * 1024 * 1024 * 1024  # 16GiB
    cache_size = sum(f.stat().st_size for f in os.scandir(CACHE_DIR) if f.is_file())
    if cache_size > threshold_size:
        logger.info(
            "Cache directory is above threshold, "
            f"deleting contents ({cache_size} bytes)"
        )
        delete_cache_dir()
        create_cache_dir()
else:
    create_cache_dir()

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

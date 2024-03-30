import sys
import logging
from typing import List

from colorlog import ColoredFormatter

log_file = "latest.log"

formatter = ColoredFormatter(
        "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s [%(name)s] %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)

file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler(sys.stdout)

file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
console_handler.setFormatter(formatter)


def configure_logger(loggers: List[str] = None): # type: ignore
    if loggers is None:
        loggers = []
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        if logger_name.startswith("strongest"):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

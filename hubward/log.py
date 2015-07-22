import logging
from colorama import Fore, Back, Style

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger()


def log(msg, indent=0, style=None):
    if style:
        start = style
        end = Style.RESET_ALL
    else:
        start = ""
        end = ""
    logger.info(start + (" " * indent) + msg + end)





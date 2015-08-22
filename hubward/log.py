import logging
from colorama import Fore, Back, Style

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger()


def log(msg, indent=0, style=None):
    """
    Generic module-level logging.

    Parameters
    ----------
    msg : string

    indent : int
        How much to indent the message. Timestamp will remain left-justified.

    style : a colorama style
        For example, use sytle=colorama.Fore.BLUE for blue text.

    """
    if style:
        start = style
        end = Style.RESET_ALL
    else:
        start = ""
        end = ""
    logger.info(start + (" " * indent) + msg + end)

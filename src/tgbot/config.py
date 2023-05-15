"""Setting up the configuration for the bot"""

import logging
import sys
from os import path
from pathlib import Path

from environs import Env, EnvError


# Change DEBUG to False when running on a production server
DEBUG: bool = True


# Path settings
_BASE_DIR: Path = Path(__file__).resolve().parent.parent
ENV_FILE: str = path.normpath(path.join(_BASE_DIR, ".env"))
LOG_FILE: str = path.normpath(path.join(_BASE_DIR, "tgbot.log"))

# According to Telegram documentation https://core.telegram.org/bots/api#sendphoto
# when sending identical files (e.g. bot logo), it is recommended not to specify path to file
# via FSInputFile(path_to_file) for methods answer_photo(), reply_photo(),
# but upload file to telegram servers and specify ID of already uploaded file.
# To get the identifier, you can send a file with an image to bot https://t.me/RawDataBot
# which in response will send the dictionary, where you need to copy the value by the 'file_id' key
BOT_LOGO_FILE_ID: str | None = "AgACAgIAAxkDAAIX9mRhAWt3RXSQKeeLYboYkLUypCjpAAJ3yTEbLwABCUtvlJhpL7_X3wEAAwIAA3gAAy8E"
BOT_LOGO: str = path.normpath(path.join(_BASE_DIR, "tgbot/assets/img/bot_logo.jpg"))

# Disables full traceback of errors in the log file
if not DEBUG:
    sys.tracebacklimit = 0

# Logger config
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=None if DEBUG else LOG_FILE,
    encoding="utf-8",
    format=f"[%(asctime)s] %(levelname)-8s {'%(filename)s:%(lineno)d - ' if DEBUG else ''}%(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO if DEBUG else logging.WARNING,
)


class BotConfig:
    """Reads variables from the .env file"""

    def __init__(self, path_to_env_file: str) -> None:
        """Initializing a class or terminating a program if no .env file is found"""
        if not path.exists(path=path_to_env_file):
            logger.critical("The .env file was not found in the path %s", path_to_env_file)
            sys.exit(1)
        self._env: Env = Env()
        self._env.read_env(path=path_to_env_file, recurse=False)

    @property
    def token(self) -> str:
        """Returns the bot token or terminates the program in case of an error"""
        try:
            return str(self._env.str("BOT_TOKEN"))
        except EnvError as exc:
            logger.critical("BOT_TOKEN not found: %s", repr(exc))
            sys.exit(repr(exc))

    @property
    def admin_ids(self) -> tuple[int, ...] | None:
        """Returns administrator IDs or None if ADMINS is not set in the .env file"""
        try:
            return tuple(map(int, self._env.list("ADMINS")))
        except (EnvError, ValueError) as exc:
            logger.warning("ADMINS ids not found: %s", repr(exc))
            return None

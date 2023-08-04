"""Setting up the configuration for the bot"""

import logging
import sys
from os import path
from pathlib import Path
from typing import NamedTuple

from environs import Env, EnvError


class WebhookCredentials(NamedTuple):
    """Represents credentials to use webhook"""

    wh_host: str
    wh_path: str
    wh_token: str
    app_host: str
    app_port: int


class Paths(NamedTuple):
    """Represents paths to directories and files used in the bot"""

    logo_path: str


# Change DEBUG to False when running on a production server
DEBUG: bool = True

# Change USE_WEBHOOK to True to use a webhook instead of long polling
USE_WEBHOOK: bool = False

# Path settings
_BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Disables full traceback of errors in the log file
if not DEBUG:
    sys.tracebacklimit = 0

# Logger config
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=None if DEBUG else path.normpath(path.join(_BASE_DIR, "tgbot.log")),
    encoding="utf-8",
    format=f"[%(asctime)s] %(levelname)-8s {'%(filename)s:%(lineno)d - ' if DEBUG else ''}%(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO if DEBUG else logging.WARNING,
)


class BotConfig:
    """Reads variables from the .env file"""

    paths: Paths = Paths(
        logo_path=path.normpath(path.join(_BASE_DIR, "tgbot/assets/img/bot_logo.jpg")),
    )

    def __init__(self) -> None:
        """Initializing a class or terminating a program if no .env file is found"""
        env_path: str = path.normpath(path.join(_BASE_DIR, ".env"))
        if not path.exists(path=env_path):
            logger.critical("The .env file was not found in the path %s", env_path)
            sys.exit(1)
        self._env: Env = Env()
        self._env.read_env(path=env_path, recurse=False)

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

    @property
    def webhook(self) -> WebhookCredentials | None:
        """Returns the credentials to use webhook"""
        try:
            return WebhookCredentials(
                wh_host=self._env.str("WEBHOOK_HOST"),
                wh_path=self._env.str("WEBHOOK_PATH"),
                wh_token=self._env.str("WEBHOOK_TOKEN"),
                app_host=self._env.str("APP_HOST"),
                app_port=self._env.int("APP_PORT"),
            ) if USE_WEBHOOK else None
        except EnvError as exc:
            logger.critical("Webhook credentials not found in the .env file: %s", repr(exc))
            sys.exit(repr(exc))

"""Setting up the configuration for the application."""

import sys
from os.path import exists
from pathlib import Path

from environs import Env, EnvError
from loguru import logger as _logger

# noinspection PyProtectedMember
from loguru._logger import Logger
from redis.asyncio import Redis

from tgbot.misc.dataclasses import Paths, WebhookCredentials

__all__: tuple[str, ...] = ("Config", "logger")


_DEBUG: bool = True  # Change DEBUG to False when running on a production server
_USE_WEBHOOK: bool = False  # Change USE_WEBHOOK to True to use a webhook instead of long polling
_USE_REDIS: bool = False  # Change USE_REDIS to True to use redis storage for FSM instead of memory
_USE_REDIS_SOCKET: bool = False  # Change to True to use a redis socket
_BASE_DIR: Path = Path(__file__).resolve().parent  # Path settings


# region Logging
class Logging:
    """Performs logging settings in the application."""

    def __init__(self, debug: bool = _DEBUG, base_dir: Path = _BASE_DIR) -> None:
        """
        Initialization of necessary parameters.

        :param debug: True, if debugging mode is enabled, otherwise False.
        :param base_dir: Path to the base directory of the application.
        """
        _time: str = "<green>{time:%Y-%m-%d %H:%M:%S}</green>"
        _level: str = "<level>{level: <8}</level>"
        _for_debug: str = "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | " if debug else ""
        _msg: str = "<level>{message}</level>"
        _log_dir: Path = Path(base_dir, "../logs")
        _log_dir.mkdir(exist_ok=True)
        _logger.remove(handler_id=0)
        _log_level: str = "DEBUG" if debug else "ERROR"
        _format: str = f"{_time} | {_level} | {_for_debug}{_msg}"
        _logger.add(sink=sys.stderr, level=_log_level, format=_format, colorize=True)
        _logger.add(sink=Path(_log_dir, "tgbot.log"), level=_log_level, format=_format, encoding="utf-8")
        self._log: Logger = _logger  # type: ignore

    @property
    def logger(self) -> Logger:
        """
        Returns the Logger object.

        :return: Logger object.
        """
        return self._log


logger: Logger = Logging().logger


# endregion


# region Config
class Config:
    """Reads variables from the .env file."""

    def __init__(
        self,
        base_dir: Path = _BASE_DIR,
        debug: bool = _DEBUG,
        use_redis: bool = _USE_REDIS,
        use_webhook: bool = _USE_WEBHOOK,
        use_redis_socket: bool = _USE_REDIS_SOCKET,
    ) -> None:
        """
        Initializing a class or raises an exception if the .env file is not found.

        :param base_dir: Path to the base directory of the application.
        :param debug: True, if debugging mode is enabled, otherwise False.
        :param use_redis: True, if Redis is used, otherwise False.
        :param use_webhook: True, if webhook is used, otherwise False.
        :param use_redis_socket: True, if a redis socket is used, otherwise False.
        :raises FileNotFoundError: if the .env file is not found.
        """
        if not debug:
            sys.tracebacklimit = 0
        self._env_path: Path = Path(base_dir, "../.env")
        if not exists(self._env_path):
            raise FileNotFoundError(f"The .env file was not found in the path: {self._env_path}")
        self._env: Env = Env()
        self._env.read_env(path=self._env_path, recurse=False)
        self._admins: list[int] = self._get_admins()
        self._paths: Paths = self._get_paths(base_dir=base_dir)
        self._redis: Redis | None = self._get_redis(use_redis=use_redis, use_socket=use_redis_socket)
        self._token: str = self._get_token()
        self._webhook: WebhookCredentials | None = self._get_webhook(use_webhook=use_webhook)

    @property
    def admins(self) -> list[int]:
        """
        Returns bots admins IDs.

        :return: list with bot admins IDs.
        """
        return self._admins

    def _get_admins(self) -> list[int]:
        """
        Returns the list of bot admin IDs.

        :return: list of bot admin IDs.
        :raises EnvError: if the admin IDs are not found in the .env file.
        """
        try:
            return list(map(int, self._env.list("ADMIN_IDS")))
        except EnvError as exc:
            raise EnvError(f"Admin IDs not found in the .env file: {repr(exc)}") from exc

    @staticmethod
    def _get_paths(base_dir: Path) -> Paths:
        """
        Returns the paths to the folders used in the program.

        :param base_dir: Path to the base directory of the application.
        :return: Paths object.
        """
        locale: Path = Path(base_dir, "locales")
        logo: Path = Path(base_dir, "assets/img/bot_logo.jpg")
        temp: Path = Path(base_dir, "temp")
        tmpl: Path = Path(base_dir, "templates")
        locale.mkdir(exist_ok=True)
        temp.mkdir(exist_ok=True)
        tmpl.mkdir(exist_ok=True)
        return Paths(locale=locale, bot_logo=logo, temp=temp, tmpl=tmpl)

    @property
    def paths(self) -> Paths:
        """
        Returns the paths to the folders used in the program.

        :return: Paths object.
        """
        return self._paths

    def _get_redis(self, use_redis: bool, use_socket: bool) -> Redis | None:
        """
        Returns an instance of the Redis class to connect to the database.

        :param use_redis: True, if Redis is used, otherwise False.
        :param use_socket: True, if a redis socket is used, otherwise False.
        :return: Redis instance or None.
        :raises EnvError: if the Redis credentials are not found in the .env file.
        """
        if not use_redis:
            return None
        try:
            db: int = self._env.int("REDIS_DB_INDEX")
            password: str = self._env.str("REDIS_DB_PASS")
            username: str = self._env.str("REDIS_DB_USER")
            if use_socket:
                unix_socket_path: str = self._env.str("REDIS_SOCKET_PATH")
                redis: Redis = Redis(db=db, password=password, unix_socket_path=unix_socket_path, username=username)
                return redis
            host: str = self._env.str("REDIS_HOST")
            port: int = self._env.int("REDIS_PORT")
            redis = Redis(host=host, port=port, db=db, password=password, username=username)
            return redis
        except EnvError as exc:
            raise EnvError(f"Redis credentials not found in the .env file: {repr(exc)}") from exc

    @property
    def redis(self) -> Redis | None:
        """
        Returns an instance of the Redis class to connect to the database.

        :return: Redis instance or None.
        """
        return self._redis

    def _get_token(self) -> str:
        """
        Returns the bot token or terminates the program in case of an error.

        :return: Telegram bot token.
        :raises EnvError: if the bot token is not found in the .env file.
        """
        try:
            return self._env.str("BOT_TOKEN")
        except EnvError as exc:
            raise EnvError(f"BOT_TOKEN not found: {repr(exc)}") from exc

    @property
    def token(self) -> str:
        """
        Returns the bot token.

        :return: Telegram bot token.
        """
        return self._token

    def _get_webhook(self, use_webhook: bool) -> WebhookCredentials | None:
        """
        Returns the credentials to use webhook.

        :param use_webhook: True, if webhook is used, otherwise False.
        :return: WebhookCredentials or None.
        :raises EnvError: if the webhook credentials are not found in the .env file.
        """
        if not use_webhook:
            return None
        try:
            return WebhookCredentials(
                wh_host=self._env.str("WEBHOOK_HOST"),
                wh_path=self._env.str("WEBHOOK_PATH"),
                wh_token=self._env.str("WEBHOOK_TOKEN"),
                app_host=self._env.str("WEBAPP_HOST"),
                app_port=self._env.int("WEBAPP_PORT"),
            )
        except EnvError as exc:
            raise EnvError(f"Webhook credentials not found in the .env file: {repr(exc)}") from exc

    @property
    def webhook(self) -> WebhookCredentials | None:
        """
        Returns the credentials to use webhook.

        :return: WebhookCredentials or None.
        """
        return self._webhook


# endregion

"""Module for working with data."""

from pathlib import Path
from typing import NamedTuple

__all__: tuple[str, ...] = ("Paths", "WebhookCredentials")


# region TelegramBot
class Paths(NamedTuple):
    """
    A class to represent paths to folders and files used in the program.

    :param locale: Path to the folder containing localization files.
    :param bot_logo: Path to the file containing the bot logo.
    :param temp: Path to the folder containing temporary files.
    :param tmpl: Path to the folder containing Jinja2 templates.
    """

    locale: Path
    bot_logo: Path
    temp: Path
    tmpl: Path


class WebhookCredentials(NamedTuple):
    """
    A class to represent data to be used by the webhook connection in the Telegram bot.

    :param wh_host: Webhook host.
    :param wh_path: Webhook path.
    :param wh_token: Webhook token.
    :param app_host: Webapp host.
    :param app_port: Webapp port.
    """

    wh_host: str
    wh_path: str
    wh_token: str
    app_host: str
    app_port: int


# endregion

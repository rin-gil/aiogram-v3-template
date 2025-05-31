"""This module implements the keyboards used in the bot."""

from tgbot.misc.tmpl_render import TmplRender

__all__: tuple[str] = ("KeyboardManager",)


class KeyboardManager:
    """Implements creation of bot keyboards."""

    def __init__(self, tmpl: TmplRender) -> None:
        """
        Initialize the keyboard manager.

        :param tmpl: TmplRender object.
        """
        self._tmpl: TmplRender = tmpl

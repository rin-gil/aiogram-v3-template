"""This module contains business logic for settings-related functionality."""

from aiogram.types import Message

from tgbot.config import Config
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender
from tgbot.services.common import BaseService

__all__: tuple[str] = ("SettingsService",)


class SettingsService(BaseService):
    """
    The class implements business logic for settings-related operations.

    :cvar _msg_settings: Path to the settings template.
    """

    _msg_settings: str = "settings/msg_settings.jinja2"

    def __init__(self, config: Config, tmpl: TmplRender, kb: KeyboardManager) -> None:
        """
        Initialize necessary parameters.

        :param config: Config object with configuration settings.
        :param tmpl: TmplRender object for rendering templates.
        :param kb: KeyboardManager object for keyboard generation.
        """
        BaseService.__init__(self, config=config, tmpl=tmpl, kb=kb)

    # region Settings menu
    async def settings(self, message: Message) -> None:
        """
        Performs actions to display user settings.

        :param message: The incoming message from the user.
        :return: None
        """
        text: str = await self._tmpl.render(tmpl=self._msg_settings, locale=message.from_user.language_code)
        # Send answer with settings menu to the user
        await message.answer(text=text)

    # endregion

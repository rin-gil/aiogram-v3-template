"""This module contains business logic for profile-related functionality."""

from aiogram.types import FSInputFile, Message

from tgbot.config import Config
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender
from tgbot.services.common import BaseService

__all__: tuple[str] = ("ProfileService",)


class ProfileService(BaseService):
    """
    The class implements business logic for profile-related operations.

    :cvar _cmd_help: Path to the help template.
    :cvar _cmd_start: Path to the start template.
    """

    _cmd_help: str = "profile/cmd_help.jinja2"
    _cmd_start: str = "profile/cmd_start.jinja2"

    def __init__(self, config: Config, tmpl: TmplRender, kb: KeyboardManager) -> None:
        """
        Initialize necessary parameters.

        :param config: Config object with configuration settings.
        :param tmpl: TmplRender object for rendering templates.
        :param kb: KeyboardManager object for keyboard generation.
        """
        BaseService.__init__(self, config=config, tmpl=tmpl, kb=kb)
        self._bot_logo: FSInputFile = FSInputFile(path=config.paths.bot_logo)

    async def start(self, message: Message) -> None:
        """
        Process incoming '/start' command.

        :param message: The incoming message from the user.
        :return: None
        """
        data: dict[str, str] = {"username": message.from_user.first_name}
        text: str = await self._tmpl.render(tmpl=self._cmd_start, locale=message.from_user.language_code, data=data)
        await message.answer(text=text)

    async def help(self, message: Message) -> None:
        """
        Process incoming '/help' command to show help information.

        :param message: The incoming message from the user.
        :return: None
        """
        data: dict[str, str] = {"username": message.from_user.first_name}
        caption: str = await self._tmpl.render(tmpl=self._cmd_help, locale=message.from_user.language_code, data=data)
        await message.answer_photo(photo=self._bot_logo, caption=caption)

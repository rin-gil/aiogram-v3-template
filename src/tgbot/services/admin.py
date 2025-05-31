"""This module contains business logic for admin-related functionality."""

from aiogram.types import Message

from tgbot.config import Config
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender
from tgbot.services.common import BaseService

__all__: tuple[str] = ("AdminService",)


class AdminService(BaseService):
    """
    The class implements business logic for admin-related operations.

    :cvar _msg_admin: Path to the admin template.
    """

    _msg_admin: str = "admin/msg_admin_panel.jinja2"

    def __init__(self, config: Config, tmpl: TmplRender, kb: KeyboardManager) -> None:
        """
        Initialize necessary parameters.

        :param config: Config object with configuration settings.
        :param tmpl: TmplRender object for rendering templates.
        :param kb: KeyboardManager object for keyboard generation.
        """
        BaseService.__init__(self, config=config, tmpl=tmpl, kb=kb)
        self._tmpl: TmplRender = tmpl
        self._kb: KeyboardManager = kb
        self._admins: list[int] = config.admins

    # region Admin menu
    async def admin_menu(self, message: Message) -> None:
        """
        Display the admin menu.

        :param message: The incoming message from the user.
        :return: None
        """
        text: str = await self._tmpl.render(tmpl=self._msg_admin, locale=message.from_user.language_code)
        await message.answer(text=text)

    # endregion

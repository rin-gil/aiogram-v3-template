"""This module contains handlers for admin-related functionality."""

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.services.admin import AdminService

__all__: tuple[str] = ("AdminHandler",)


class AdminHandler:
    """The class implements handlers for admin-related user interactions."""

    def __init__(self, service: AdminService) -> None:
        """
        Initialize necessary parameters.

        :param service: AdminService object for business logic.
        """
        self._service: AdminService = service

    # region Admin menu

    async def cmd_admin(self, message: Message, state: FSMContext) -> None:
        """
        Handle the '/admin' command to show the admin menu.

        :param message: The incoming message from the user.
        :param state: The Finite State Machine (FSM) context for managing user states.
        :return: None
        """
        await message.delete()
        await state.clear()
        await self._service.admin_menu(message=message)

    # endregion

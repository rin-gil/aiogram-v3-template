"""This module contains handlers for settings-related functionality."""

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.services.settings import SettingsService

__all__: tuple[str] = ("SettingsHandler",)


class SettingsHandler:
    """The class implements handlers for settings-related user interactions."""

    def __init__(self, service: SettingsService) -> None:
        """
        Initialize necessary parameters.

        :param service: SettingsService object for business logic.
        """
        self._service: SettingsService = service

    # region Settings menu
    async def cmd_or_msg_settings(self, message: Message, state: FSMContext) -> None:
        """
        Handle the '/settings' command to show user settings.

        :param message: The incoming message from the user.
        :param state: The Finite State Machine (FSM) context for managing user states.
        :return: None
        """
        await message.delete()
        await state.clear()
        await self._service.settings(message=message)

    # endregion

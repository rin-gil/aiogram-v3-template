"""This module contains handlers for profile-related functionality."""

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.services.profile import ProfileService

__all__: tuple[str] = ("ProfileHandler",)


class ProfileHandler:
    """The class implements handlers for profile-related user interactions."""

    def __init__(self, service: ProfileService) -> None:
        """
        Initialize necessary parameters.

        :param service: ProfileService object for business logic.
        """
        self._service: ProfileService = service

    async def cmd_start(self, message: Message, state: FSMContext) -> None:
        """
        Handle the '/start' command.

        :param message: The incoming message from the user.
        :param state: The Finite State Machine (FSM) context for managing user states.
        :return: None
        """
        await state.clear()
        await message.delete()
        await self._service.start(message=message)

    async def cmd_help(self, message: Message) -> None:
        """
        Handle the '/help' command.

        :param message: The incoming message from the user.
        :return: None
        """
        await message.delete()
        await self._service.help(message=message)

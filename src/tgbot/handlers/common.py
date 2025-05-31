"""This module contains common handlers for general bot functionality."""

from aiogram.types import Message

from tgbot.services.common import BaseService

__all__: tuple[str] = ("CommonHandler",)


class CommonHandler:
    """The class implements common handlers for general bot interactions."""

    def __init__(self, service: BaseService) -> None:
        """
        Initialize necessary parameters.

        :param service: BaseService object for business logic.
        """
        self._service: BaseService = service

    async def any_delete(self, message: Message) -> None:
        """
        Deletes content sent by a user if the bot should not respond to it.

        :param message: The incoming message from the user.
        :return: None
        """
        await self._service.any_delete(message=message)

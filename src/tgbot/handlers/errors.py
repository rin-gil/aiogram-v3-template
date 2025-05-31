"""Handler of errors that are not caught by other functions."""

from aiogram.handlers import ErrorHandler
from aiogram.types import CallbackQuery, ErrorEvent, Message

from tgbot.config import logger

__all__: tuple[str, ...] = ("ErrHandler",)


class ErrHandler(ErrorHandler):
    """Class for errors handlers that are not caught by other functions."""

    async def handle(self) -> None:
        """
        Logs exceptions that are not handled by other functions.

        :return: None
        """
        # noinspection PyTypeChecker
        event: ErrorEvent = self.event  # type: ignore
        msg_or_call_from_user: str = (
            f", Message: {event.update.message.text}"
            if isinstance(event.update.message, Message)
            else (
                f", Callback: {event.update.callback_query.data}"  # type: ignore
                if isinstance(event.update.callback_query, CallbackQuery)
                else ""
            )
        )
        logger.error(f"Exception while handling an update: {event.exception} {msg_or_call_from_user}")

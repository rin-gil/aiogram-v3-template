"""
Handler of errors that are not caught by other functions

Writes an error message into the log, as well as the text of the message or callback from the user of the bot,
during the processing of which an error occurred
"""

from aiogram import Router
from aiogram.types import CallbackQuery, ErrorEvent, Message

from tgbot.config import logger


async def error_handler(event: ErrorEvent) -> bool:
    """Logs exceptions that are not handled by other functions"""
    if isinstance(event.update.message, Message):
        msg_or_call_from_user: str = f", Message: {event.update.message.text}"
    elif isinstance(event.update.callback_query, CallbackQuery):
        msg_or_call_from_user = f", Callback: {event.update.callback_query.data}"
    else:
        msg_or_call_from_user = ""
    logger.error("Exception while handling an update: %s%s", event.exception, msg_or_call_from_user)
    return True


# Create and register router
error_router: Router = Router(name="error_router")
error_router.errors.register(error_handler)

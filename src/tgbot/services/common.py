"""This module contains base service classes for shared functionality."""

from asyncio import sleep

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from tgbot.config import Config
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender

__all__: tuple[str] = ("BaseService",)


class BaseService:
    """
    Base service class with shared functionality for other services.

    :cvar _msg_expired_action: Path to the expired action template.
    :cvar _msg_unsupported: Path to the unsupported template.
    """

    _msg_expired_action: str = "common/msg_expired_action.jinja2"
    _msg_unsupported: str = "common/msg_unsupported.jinja2"

    def __init__(self, config: Config, tmpl: TmplRender, kb: KeyboardManager) -> None:
        """
        Initialize shared dependencies for services.

        :param config: Config object with configuration settings.
        :param tmpl: TmplRender object for rendering templates.
        :param kb: KeyboardManager object for keyboard generation.
        """
        self._config: Config = config
        self._tmpl: TmplRender = tmpl
        self._kb: KeyboardManager = kb

    # region Public methods
    async def any_delete(self, message: Message) -> None:
        """
        Deletes content sent by a user if the bot should not respond to it.

        :param message: The incoming message from the user.
        :return: None
        """
        text: str = await self._tmpl.render(tmpl=self._msg_unsupported, locale=message.from_user.language_code)
        msg: Message = await message.reply(text=text)
        await sleep(delay=3)
        await msg.delete()
        await message.delete()

    # endregion

    # region Private methods
    async def _edit_or_send_callback(
        self, call: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> Message:
        """
        Edit the existing message from a callback if possible, otherwise send a new one.
        Shows a fixed alert "Action expired" if editing fails (e.g., message older than 48 hours).

        :param call: The callback query to edit or reply to.
        :param text: The text to send or edit into the message.
        :param reply_markup: The keyboard markup to include (optional).
        :return: The edited message or a new one.
        """
        # Trying to edit an existing message, if it does not exist or 48 hours have passed, the try will fail
        try:
            msg: Message = await call.message.edit_text(text=text, reply_markup=reply_markup)  # type: ignore
            await call.answer()
        # If the message is too old, send a new one
        except TelegramBadRequest as e:
            # If the message as same as a current content
            if "the same as a current content" in e.message:
                await call.answer()
                return call.message  # type: ignore
            # If the message not as same as a current content
            alert_text: str = await self._tmpl.render(
                tmpl=self._msg_expired_action, locale=call.from_user.language_code
            )
            await call.answer(text=alert_text, show_alert=True)
            msg = await call.message.answer(text=text, reply_markup=reply_markup)
        return msg

    @staticmethod
    async def _edit_or_send_msg(
        bot: Bot, chat_id: int, msg_id: int, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> Message:
        """
        Edit the existing message if possible, otherwise send a new one.

        :param bot: The bot instance.
        :param chat_id: The chat ID to send the message to.
        :param msg_id: The message ID to edit.
        :param text: The text to edit into the message.
        :param reply_markup: The keyboard markup to include (optional).
        :return: The edited message or a new one.
        """
        # Trying to edit an existing message, if it does not exist or 48 hours have passed, the try will fail
        try:
            msg: Message = await bot.edit_message_text(  # type: ignore
                chat_id=chat_id, message_id=msg_id, text=text, reply_markup=reply_markup
            )
        # If the message is too old, send a new one
        except TelegramBadRequest:
            msg = await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        return msg

    # endregion

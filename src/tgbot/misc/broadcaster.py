"""The module contains a simple broadcaster with rate limiting for sending messages to bot users."""

from asyncio import Queue, sleep
from typing import Any, Literal

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import InlineKeyboardMarkup, Message

from tgbot.config import logger
from tgbot.misc.decorators import handle_telegram_exc, handle_exc

__all__: tuple[str] = ("Broadcaster",)


class Broadcaster:
    """
    Implements rate-limited message broadcasting to bot users using Singleton pattern.

    :cvar _instance: Singleton instance of the Broadcaster.
    :cvar _max_msgs_per_sec: Maximum number of messages per second allowed by Telegram (set to 25 for safety).
    """

    _instance: "Broadcaster" = None
    _max_msgs_per_sec: int = 20

    def __new__(cls, *args: Any, **kwargs: Any) -> "Broadcaster":
        """
        Implement the Singleton pattern. The method ensures that only one instance of the class is created.

        :param args: Arguments for the class constructor.
        :param kwargs: Keyword arguments for the class constructor.
        :return: The single instance of the class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, bot: Bot) -> None:
        """
        Initialize the broadcaster with bot and database instances.

        :param bot: Bot object.
        """
        if not hasattr(self, "_initialized"):
            self._bot: Bot = bot
            self._message_queue: Queue = Queue()
            self._processing: bool = False
            self._initialized: bool = True

    @handle_telegram_exc
    async def send_content(
        self,
        user_id: int,
        msg: str | None = None,
        content_type: Literal["text", "chat_action"] = "text",
        notify: bool = True,
        reply_markup: InlineKeyboardMarkup | None = None,
        reply_to_message_id: int | None = None,
    ) -> int | None:
        """
        Queue a message to be sent with rate limiting.

        :param user_id: Telegram user id.
        :param msg: Message text.
        :param content_type: Type of content ("text" or "chat_action").
        :param notify: Notification on or off.
        :param reply_markup: Optional inline keyboard markup.
        :param reply_to_message_id: Optional message ID to reply to.
        :return: Message ID if content_type is "text" and message was sent, None otherwise.
        """
        await self._message_queue.put(item=(user_id, msg, content_type, notify, reply_markup, reply_to_message_id))
        if not self._processing:
            self._processing = True
            message_id: int | None = None
            try:
                while not self._message_queue.empty():
                    args: tuple[
                        int, str | None, Literal["text", "chat_action"], bool, InlineKeyboardMarkup | None, int | None
                    ] = await self._message_queue.get()
                    message_id = await self._send_single_content(*args)
                    self._message_queue.task_done()
                    await sleep(1.0 / self._max_msgs_per_sec)
                return message_id
            finally:
                self._processing = False
        return None

    async def _send_single_content(
        self,
        user_id: int,
        msg: str | None,
        content_type: Literal["text", "chat_action"],
        notify: bool,
        reply_markup: InlineKeyboardMarkup | None,
        reply_to_message_id: int | None,
    ) -> int | None:
        """
        Internal method to send a single message or perform a chat action.

        :param user_id: Telegram user id to send the message to.
        :param msg: Message text.
        :param content_type: Type of content ("text" or "chat_action").
        :param notify: Whether to send the message with notification.
        :param reply_markup: Optional inline keyboard markup.
        :param reply_to_message_id: Optional message ID to reply to.
        :return: Message ID if content_type is "text" and message was sent, None otherwise.
        """
        if content_type == "text":
            if msg:  # Send a text message to the user
                message: Message = await self._bot.send_message(
                    chat_id=user_id,
                    text=msg[:4096],
                    disable_notification=not notify,
                    reply_markup=reply_markup,
                    reply_to_message_id=reply_to_message_id,
                )
                return message.message_id
            logger.error("Text message cannot be empty")  # Log an error if the text message is empty
            return None
        if content_type == "chat_action":  # Send a chat action (e.g., typing indicator)
            await self._bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            return None
        logger.error(f"Unsupported content type: {content_type}")  # Log an error for unsupported content types
        return None

    @handle_exc
    async def broadcast(
        self,
        users_ids: list[int],
        msg: str | None,
        content_type: Literal["text", "chat_action"] = "text",
        notify: bool = True,
        reply_markup: InlineKeyboardMarkup | None = None,
        reply_to_message_id: int | None = None,
    ) -> None:
        """
        Broadcast messages to multiple users with rate limiting.

        :param users_ids: List of telegram user ids.
        :param msg: Message text.
        :param content_type: Type of content ("text" or "chat_action").
        :param notify: Notification on or off.
        :param reply_markup: Optional inline keyboard markup.
        :param reply_to_message_id: Optional message ID to reply to.
        :return: None
        """
        for user_id in users_ids:
            await self.send_content(
                user_id=user_id,
                msg=msg,
                content_type=content_type,
                notify=notify,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )

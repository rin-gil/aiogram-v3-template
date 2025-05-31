"""Unit tests for src/tgbot/misc/broadcaster.py"""

# pylint: disable=redefined-outer-name

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramAPIError
from aiogram.methods.send_message import SendMessage
from aiogram.types import Chat, InlineKeyboardMarkup, InlineKeyboardButton, Message

from tgbot.misc.broadcaster import Broadcaster

__all__: tuple = ()


@pytest.fixture
def mock_bot() -> Bot:
    """
    Fixture to create a mock Bot object with a valid token.

    :return: Mock instance of the Bot class.
    """
    return Bot(token="123456789:mock_token")


@pytest.fixture
def broadcaster(mock_bot: Bot) -> Broadcaster:
    """
    Fixture to create a Broadcaster instance with mock objects.

    :param mock_bot: Fixture providing a mock Bot instance.
    :return: Broadcaster instance.
    """
    return Broadcaster(bot=mock_bot)


@pytest.mark.asyncio
@pytest.mark.parametrize("msg, notify, expected_notify", [("Test message", True, False), ("Test message", False, True)])
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_send_content_text(
    mock_send_message: AsyncMock, broadcaster: Broadcaster, msg: str, notify: bool, expected_notify: bool
) -> None:
    """
    Test send_content with text message for different notification settings.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :param msg: Message text to send.
    :param notify: Notification setting.
    :param expected_notify: Expected disable_notification value.
    :return: None
    """
    mock_send_message.return_value = Message(message_id=123, chat=Chat(id=123, type="private"), date=datetime.now())
    message_id: int = await broadcaster.send_content(user_id=123, msg=msg, content_type="text", notify=notify)
    mock_send_message.assert_called_once_with(
        chat_id=123,
        text="Test message",
        disable_notification=expected_notify,
        reply_markup=None,
        reply_to_message_id=None,
    )
    assert message_id == 123


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_send_content_with_keyboard(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test send_content with text message and inline keyboard.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Click", callback_data="test")]]
    )
    mock_send_message.return_value = Message(message_id=123, chat=Chat(id=123, type="private"), date=datetime.now())
    message_id: int = await broadcaster.send_content(
        user_id=123, msg="Test with keyboard", content_type="text", reply_markup=keyboard
    )
    mock_send_message.assert_called_once_with(
        chat_id=123,
        text="Test with keyboard",
        disable_notification=False,
        reply_markup=keyboard,
        reply_to_message_id=None,
    )
    assert message_id == 123


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_chat_action", new_callable=AsyncMock)
async def test_send_content_chat_action(mock_send_chat_action: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test send_content with chat_action content type.

    :param mock_send_chat_action: Mocked send_chat_action method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    message_id: int = await broadcaster.send_content(user_id=123, content_type="chat_action")
    mock_send_chat_action.assert_called_once_with(chat_id=123, action=ChatAction.TYPING)
    assert message_id is None


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_send_content_empty_text(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test send_content with empty text message.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    message_id: int = await broadcaster.send_content(user_id=123, msg=None, content_type="text")
    mock_send_message.assert_not_called()
    assert message_id is None


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
@patch.object(target=Bot, attribute="send_chat_action", new_callable=AsyncMock)
async def test_send_content_unsupported_type(
    mock_send_chat_action: AsyncMock, mock_send_message: AsyncMock, broadcaster: Broadcaster
) -> None:
    """
    Test send_content with unsupported content type.

    :param mock_send_chat_action: Mocked send_chat_action method.
    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    message_id: int = await broadcaster.send_content(user_id=123, content_type="audio")  # type: ignore
    mock_send_message.assert_not_called()
    mock_send_chat_action.assert_not_called()
    assert message_id is None


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_send_content_telegram_error(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test send_content when Telegram API raises an exception, handled by decorator.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    mock_send_message.side_effect = TelegramAPIError(
        message="Telegram API error", method=SendMessage(chat_id=123, text="Test message")
    )
    message_id: int = await broadcaster.send_content(user_id=123, msg="Test message", content_type="text")
    assert message_id == 0


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_broadcast_success(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test broadcast with successful message sending, including reply_to_message_id.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Test", callback_data="test")]]
    )
    mock_send_message.side_effect = [
        Message(message_id=1, chat=Chat(id=123, type="private"), date=datetime.now()),
        Message(message_id=2, chat=Chat(id=456, type="private"), date=datetime.now()),
    ]
    await broadcaster.broadcast(
        users_ids=[123, 456], msg="Test broadcast", reply_markup=keyboard, reply_to_message_id=789
    )
    assert mock_send_message.call_count == 2
    mock_send_message.assert_any_call(
        chat_id=123, text="Test broadcast", disable_notification=False, reply_markup=keyboard, reply_to_message_id=789
    )
    mock_send_message.assert_any_call(
        chat_id=456, text="Test broadcast", disable_notification=False, reply_markup=keyboard, reply_to_message_id=789
    )


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_broadcast_partial_failure(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test broadcast with partial failure in sending messages.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    mock_send_message.side_effect = [
        Message(message_id=1, chat=Chat(id=123, type="private"), date=datetime.now()),
        TelegramAPIError(message="Telegram API error", method=SendMessage(chat_id=456, text="Test broadcast")),
    ]
    await broadcaster.broadcast(users_ids=[123, 456], msg="Test broadcast")
    assert mock_send_message.call_count == 2


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_broadcast_empty_users(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test broadcast with an empty list of users.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    await broadcaster.broadcast(users_ids=[], msg="Test broadcast")
    mock_send_message.assert_not_called()


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_rate_limiting(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test that the broadcaster respects rate limiting.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    mock_send_message.side_effect = [
        Message(message_id=1, chat=Chat(id=123, type="private"), date=datetime.now()),
        Message(message_id=2, chat=Chat(id=456, type="private"), date=datetime.now()),
        Message(message_id=3, chat=Chat(id=789, type="private"), date=datetime.now()),
    ]
    start_time: datetime = datetime.now()
    await broadcaster.broadcast(users_ids=[123, 456, 789], msg="Test rate limiting")
    end_time: datetime = datetime.now()
    duration: float = (end_time - start_time).total_seconds()
    # 3 messages at 20 messages/sec should take at least 0.1 seconds (2 intervals of 0.05s)
    assert duration >= 0.1
    assert mock_send_message.call_count == 3


@pytest.mark.asyncio
@patch.object(target=Bot, attribute="send_message", new_callable=AsyncMock)
async def test_send_content_with_reply_to_message_id(mock_send_message: AsyncMock, broadcaster: Broadcaster) -> None:
    """
    Test send_content with text message and reply_to_message_id.

    :param mock_send_message: Mocked send_message method.
    :param broadcaster: Fixture providing a Broadcaster instance.
    :return: None
    """
    mock_send_message.return_value = Message(message_id=123, chat=Chat(id=123, type="private"), date=datetime.now())
    message_id: int = await broadcaster.send_content(
        user_id=123, msg="Test with reply", content_type="text", reply_to_message_id=456
    )
    mock_send_message.assert_called_once_with(
        chat_id=123, text="Test with reply", disable_notification=False, reply_markup=None, reply_to_message_id=456
    )
    assert message_id == 123

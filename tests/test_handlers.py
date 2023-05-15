"""Tests for the handlers package"""

from typing import Any

import pytest
from aiogram import Bot, Dispatcher
from aiogram.methods import SendPhoto, SendMessage
from aiogram.types import Chat, User

from src.tgbot.config import BOT_LOGO_FILE_ID, BotConfig, ENV_FILE  # pylint: disable=import-error
from tests.utils.fake_data import get_message, get_update  # pylint: disable=import-error


@pytest.mark.asyncio
async def test_start_cmd_handler(bot: Bot, dispatcher: Dispatcher) -> None:
    """Tests the response to the '/start' command from bot users and admins"""
    config: BotConfig = BotConfig(path_to_env_file=ENV_FILE)

    # Handler test if the sender is a user
    result: Any = await dispatcher.feed_update(
        bot=bot, update=get_update(message=get_message(text="/start")), config=config
    )
    expected_text: str = "👋 Hello, Test!"
    assert isinstance(result, SendMessage)
    assert result.text == expected_text

    # Handler test if the sender is an admin
    admin_id: int = config.admin_ids[0]
    test_admin: User = User(id=admin_id, is_bot=False, first_name="TestAdmin", username="test_admin")
    test_admin_chat: Chat = Chat(
        id=123456789, type="private", username=test_admin.username, first_name=test_admin.first_name
    )
    result = await dispatcher.feed_update(
        bot=bot,
        update=get_update(message=get_message(text="/start", from_user=test_admin, chat=test_admin_chat)),
        config=BotConfig(path_to_env_file=ENV_FILE),
    )
    expected_text = "👋 Hello, admin!"
    assert isinstance(result, SendMessage)
    assert result.text == expected_text


@pytest.mark.asyncio
async def test_help_cmd_handler(bot: Bot, dispatcher: Dispatcher) -> None:
    """Tests the response to the '/help' command"""
    result: Any = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text="/help")))
    expected_caption: str = (
        "This is a template for a telegram bot written in Python using the "
        "<b><a href='https://github.com/aiogram/aiogram'>aiogram</a></b> framework"
        "\n\n"
        "The source code of the template is"
        " available in the repository on <b><a href='https://github.com/rin-gil/aiogram_v3_template'>GitHub</a></b>"
    )
    expected_photo: str = BOT_LOGO_FILE_ID
    assert isinstance(result, SendPhoto)
    assert result.caption == expected_caption
    assert result.photo == expected_photo


@pytest.mark.asyncio
async def test_echo_handler(dispatcher: Dispatcher, bot: Bot) -> None:
    """Tests the response to the text and unknown commands"""
    input_text: str = "test text"
    result: Any = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text=input_text)))
    expected_text: str = f"<pre>{input_text}</pre>"
    assert isinstance(result, SendMessage)
    assert result.text == expected_text

    input_text = "/unknown_cmd"
    result = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text=input_text)))
    expected_text = f"<pre>{input_text}</pre>"
    assert isinstance(result, SendMessage)
    assert result.text == expected_text

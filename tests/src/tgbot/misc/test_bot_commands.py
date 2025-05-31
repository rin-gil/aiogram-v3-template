# type: ignore
"""Unit tests for src/tgbot/misc/bot_commands.py"""

# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
# pylint: disable=duplicate-code

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats, BotCommandScopeChat

from tgbot.misc.bot_commands import BotCommands
from tgbot.misc.tmpl_render import TmplRender

__all__: tuple = ()


@pytest.fixture
async def mock_bot() -> AsyncGenerator[Bot, None]:
    """
    Provides a mocked Bot instance for testing.

    :return: A mocked Bot instance.
    """
    bot: MagicMock = MagicMock(spec=Bot)
    bot.set_my_commands = AsyncMock(return_value=None)
    yield bot


@pytest.fixture
async def mock_tmpl_render() -> AsyncGenerator[TmplRender, None]:
    """
    Provides a mocked TmplRender instance for testing.

    :return: A mocked TmplRender instance.
    """
    tmpl_render: MagicMock = MagicMock(spec=TmplRender)

    def render_side_effect(tmpl: str, locale: str) -> str:
        """
        Side effect for 'render' method of 'TmplRender' mock.

        Depending on the template name, returns a corresponding description.
        If the template name is unknown, returns an empty string.

        :param tmpl: The template name to render.
        :param locale: The locale to render for.
        :return: The rendered template as a string.
        """
        if tmpl == "common/cmd_start.jinja2":
            return "Start description"
        if tmpl == "common/cmd_help.jinja2":
            return "Help description"
        if tmpl == "common/cmd_settings.jinja2":
            return "Settings description"
        if tmpl == "admin/cmd_admin.jinja2":
            return "Admin description"
        return ""

    tmpl_render.render = AsyncMock(side_effect=render_side_effect)
    tmpl_render.get_locales = AsyncMock(return_value=["en", "ru"])
    yield tmpl_render


@pytest.fixture
async def bot_commands(mock_bot: Bot, mock_tmpl_render: TmplRender) -> BotCommands:
    """
    Provides a BotCommands instance with mocked dependencies.

    :param mock_bot: A mocked Bot instance.
    :param mock_tmpl_render: A mocked TmplRender instance.
    :return: An instance of BotCommands.
    """
    return BotCommands(bot=mock_bot, tmpl_render=mock_tmpl_render, admin_ids=[123, 456])


@pytest.mark.asyncio
async def test_init(bot_commands: BotCommands, mock_bot: Bot, mock_tmpl_render: TmplRender) -> None:
    """
    Tests the __init__ method of BotCommands.

    :param bot_commands: The BotCommands instance to test.
    :param mock_bot: The mocked Bot instance.
    :param mock_tmpl_render: The mocked TmplRender instance.
    :return: None
    """
    assert bot_commands._bot is mock_bot
    assert bot_commands._tmpl is mock_tmpl_render
    assert bot_commands._admin_ids == [123, 456]


# noinspection PyUnresolvedReferences
@pytest.mark.asyncio
@pytest.mark.parametrize("lang_code", ["en", "ru"])
async def test_get_commands(bot_commands: BotCommands, mock_tmpl_render: TmplRender, lang_code: str) -> None:
    """
    Tests the _get_commands method of BotCommands.

    :param bot_commands: The BotCommands instance to test.
    :param mock_tmpl_render: The mocked TmplRender instance.
    :param lang_code: The language code to test.
    :return: None
    """
    result: list[BotCommand] = await bot_commands._get_commands(lang_code=lang_code)
    expected: list[BotCommand] = [
        BotCommand(command="start", description="Start description"),
        BotCommand(command="help", description="Help description"),
        BotCommand(command="settings", description="Settings description"),
    ]
    assert result == expected
    assert mock_tmpl_render.render.call_count == 3
    mock_tmpl_render.render.assert_any_call(tmpl="common/cmd_start.jinja2", locale=lang_code)
    mock_tmpl_render.render.assert_any_call(tmpl="common/cmd_help.jinja2", locale=lang_code)
    mock_tmpl_render.render.assert_any_call(tmpl="common/cmd_settings.jinja2", locale=lang_code)


# noinspection PyUnresolvedReferences
@pytest.mark.asyncio
@pytest.mark.parametrize("lang_code", ["en", "ru"])
async def test_get_admins_commands(bot_commands: BotCommands, mock_tmpl_render: TmplRender, lang_code: str) -> None:
    """
    Tests the _get_admins_commands method of BotCommands.

    :param bot_commands: The BotCommands instance to test.
    :param mock_tmpl_render: The mocked TmplRender instance.
    :param lang_code: The language code to test.
    :return: None
    """
    result: list[BotCommand] = await bot_commands._get_admins_commands(lang_code=lang_code)
    expected: list[BotCommand] = [BotCommand(command="admin", description="Admin description")]
    assert result == expected
    mock_tmpl_render.render.assert_called_once_with(tmpl="admin/cmd_admin.jinja2", locale=lang_code)


# noinspection PyUnresolvedReferences
@pytest.mark.asyncio
async def test_set_commands(bot_commands: BotCommands, mock_tmpl_render: TmplRender, mock_bot: Bot) -> None:
    """
    Tests the set_commands method of BotCommands.

    :param bot_commands: The BotCommands instance to test.
    :param mock_tmpl_render: The mocked TmplRender instance.
    :param mock_bot: The mocked Bot instance.
    :return: None
    """
    await bot_commands.set_commands()
    # Check group chats commands cleanup
    mock_bot.set_my_commands.assert_any_call(commands=[], scope=BotCommandScopeAllGroupChats())
    # Check private chats commands cleanup
    mock_bot.set_my_commands.assert_any_call(commands=[], scope=BotCommandScopeAllPrivateChats())
    # Check private chats commands for each locale
    expected_commands: list[BotCommand] = [
        BotCommand(command="start", description="Start description"),
        BotCommand(command="help", description="Help description"),
        BotCommand(command="settings", description="Settings description"),
    ]
    mock_bot.set_my_commands.assert_any_call(
        commands=expected_commands, language_code="en", scope=BotCommandScopeAllPrivateChats()
    )
    mock_bot.set_my_commands.assert_any_call(
        commands=expected_commands, language_code="ru", scope=BotCommandScopeAllPrivateChats()
    )
    # Check admin commands for each admin ID and locale
    expected_admin_commands: list[BotCommand] = [
        BotCommand(command="start", description="Start description"),
        BotCommand(command="help", description="Help description"),
        BotCommand(command="settings", description="Settings description"),
        BotCommand(command="admin", description="Admin description"),
    ]
    for admin_id in [123, 456]:
        for locale in ["en", "ru"]:
            mock_bot.set_my_commands.assert_any_call(
                commands=expected_admin_commands, language_code=locale, scope=BotCommandScopeChat(chat_id=admin_id)
            )
    assert mock_tmpl_render.get_locales.call_count == 1
    assert mock_tmpl_render.render.call_count == 10
    assert mock_bot.set_my_commands.call_count == 8


# noinspection PyUnresolvedReferences
@pytest.mark.asyncio
async def test_set_commands_no_locales(mock_bot: Bot, mock_tmpl_render: TmplRender) -> None:
    """
    Tests the set_commands method of BotCommands when no locales are available.

    :param mock_bot: The mocked Bot instance.
    :param mock_tmpl_render: The mocked TmplRender instance.
    :return: None
    """
    mock_tmpl_render.get_locales = AsyncMock(return_value=[])
    bot_commands: BotCommands = BotCommands(bot=mock_bot, tmpl_render=mock_tmpl_render, admin_ids=[123])
    await bot_commands.set_commands()
    # Check group chats commands cleanup
    mock_bot.set_my_commands.assert_any_call(commands=[], scope=BotCommandScopeAllGroupChats())
    # Check private chats commands cleanup
    mock_bot.set_my_commands.assert_any_call(commands=[], scope=BotCommandScopeAllPrivateChats())
    # Check that no commands are set for private chats or admins
    assert mock_tmpl_render.render.call_count == 0
    assert mock_bot.set_my_commands.call_count == 2  # Only cleanup calls


# noinspection PyUnresolvedReferences
@pytest.mark.asyncio
async def test_set_commands_empty_admin_ids(mock_bot: Bot, mock_tmpl_render: TmplRender) -> None:
    """
    Tests the set_commands method of BotCommands with an empty admin_ids list.

    :param mock_bot: The mocked Bot instance.
    :param mock_tmpl_render: The mocked TmplRender instance.
    :return: None
    """
    bot_commands: BotCommands = BotCommands(bot=mock_bot, tmpl_render=mock_tmpl_render, admin_ids=[])
    await bot_commands.set_commands()
    # Check group chats commands cleanup
    mock_bot.set_my_commands.assert_any_call(commands=[], scope=BotCommandScopeAllGroupChats())
    # Check private chats commands cleanup
    mock_bot.set_my_commands.assert_any_call(commands=[], scope=BotCommandScopeAllPrivateChats())
    # Check private chats commands for each locale
    expected_commands: list[BotCommand] = [
        BotCommand(command="start", description="Start description"),
        BotCommand(command="help", description="Help description"),
        BotCommand(command="settings", description="Settings description"),
    ]
    mock_bot.set_my_commands.assert_any_call(
        commands=expected_commands, language_code="en", scope=BotCommandScopeAllPrivateChats()
    )
    mock_bot.set_my_commands.assert_any_call(
        commands=expected_commands, language_code="ru", scope=BotCommandScopeAllPrivateChats()
    )
    assert mock_tmpl_render.get_locales.call_count == 1
    assert mock_tmpl_render.render.call_count == 6  # 3 per locale (en, ru)
    assert mock_bot.set_my_commands.call_count == 4  # 1 group + 1 private + 2 locales

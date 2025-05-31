# type: ignore
"""Unit tests for src/bot.py"""

# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

from asyncio import AbstractEventLoop, sleep
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

# noinspection PyProtectedMember
from bot import main, TgBot
from tgbot.config import Config
from tgbot.misc.broadcaster import Broadcaster
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.scheduler import Scheduler
from tgbot.misc.tmpl_render import TmplRender

__all__: tuple = ()


@pytest.fixture
def mock_loop() -> AbstractEventLoop:
    """
    Fixture to provide a mock event loop.

    :return: Mock event loop instance.
    """
    return AsyncMock()


# noinspection PyProtectedMember
@pytest.fixture
def tg_bot() -> TgBot:
    """
    Provide a fresh TgBot instance for each test with mocked dependencies, using RedisStorage.

    :return: TgBot instance.
    """
    with patch(target="bot.Config", return_value=MagicMock(spec=Config)) as mock_config, patch(
        target="bot.Bot", return_value=MagicMock(spec=Bot)
    ) as mock_bot:
        mock_config.return_value.token = "mock_token"
        mock_config.return_value.redis = MagicMock()  # Enable Redis to use RedisStorage
        mock_config.return_value.admins = [123, 456]
        mock_config.return_value.paths = MagicMock()
        mock_config.return_value.webhook = None
        bot_instance: TgBot = TgBot()
        bot_instance._bot = mock_bot.return_value
        bot_instance._bot.default = DefaultBotProperties(
            parse_mode="HTML", allow_sending_without_reply=True, link_preview_is_disabled=True
        )
        bot_instance._bot.session = MagicMock()
        bot_instance._bot.session.close = AsyncMock()  # Only close remains asynchronous
        yield bot_instance
        Broadcaster._instance = None


def test_init(tg_bot: TgBot) -> None:
    """
    Tests initialization of TgBot with RedisStorage.

    :param tg_bot: Instance of TgBot to test.
    :return: None
    """
    assert isinstance(tg_bot._config, Config)
    assert isinstance(tg_bot._bot, Bot)
    assert isinstance(tg_bot._dp, Dispatcher)
    assert isinstance(tg_bot._broadcaster, Broadcaster)
    assert isinstance(tg_bot._tmpl, TmplRender)
    assert isinstance(tg_bot._kb, KeyboardManager)
    assert isinstance(tg_bot._scheduler, Scheduler)
    assert isinstance(tg_bot._dp.storage, RedisStorage)
    assert tg_bot._bot.default == DefaultBotProperties(
        parse_mode="HTML", allow_sending_without_reply=True, link_preview_is_disabled=True
    )


# noinspection PyUnresolvedReferences,PyPropertyAccess
@pytest.mark.asyncio
async def test_on_startup_polling(tg_bot: TgBot) -> None:
    """
    Tests the on_startup method in polling mode.

    :param tg_bot: Instance of TgBot to test.
    :return: None
    """
    tg_bot._broadcaster.broadcast = AsyncMock()
    tg_bot._scheduler.schedule = AsyncMock()
    mock_bot_commands: MagicMock = MagicMock()
    mock_bot_commands.set_commands = AsyncMock()
    tg_bot._config.webhook = None
    with patch(target="bot.BotCommands", return_value=mock_bot_commands):
        await tg_bot._on_startup()
    tg_bot._broadcaster.broadcast.assert_called_once_with(
        users_ids=tg_bot._config.admins, msg="Bot was started", notify=False
    )
    tg_bot._scheduler.schedule.assert_called_once()
    mock_bot_commands.set_commands.assert_called_once()
    tg_bot._bot.set_webhook.assert_not_called()


# noinspection PyUnresolvedReferences,PyPropertyAccess
@pytest.mark.asyncio
async def test_on_startup_webhook(tg_bot: TgBot) -> None:
    """
    Tests the on_startup method in webhook mode.

    :param tg_bot: Instance of TgBot to test.
    :return: None
    """
    tg_bot._broadcaster.broadcast = AsyncMock()
    tg_bot._scheduler.schedule = AsyncMock()
    mock_bot_commands: MagicMock = MagicMock()
    mock_bot_commands.set_commands = AsyncMock()
    tg_bot._config.webhook = MagicMock()
    tg_bot._config.webhook.wh_host = "https://example.com"
    tg_bot._config.webhook.wh_path = "webhook_path"
    tg_bot._config.webhook.wh_token = "mock_token"
    with patch(target="bot.BotCommands", return_value=mock_bot_commands):
        await tg_bot._on_startup()
    tg_bot._broadcaster.broadcast.assert_called_once_with(
        users_ids=tg_bot._config.admins, msg="Bot was started", notify=False
    )
    tg_bot._scheduler.schedule.assert_called_once()
    mock_bot_commands.set_commands.assert_called_once()
    tg_bot._bot.set_webhook.assert_called_once_with(
        url="https://example.com/webhook_path", drop_pending_updates=False, secret_token="mock_token"
    )


# noinspection PyUnresolvedReferences,PyPropertyAccess
@pytest.mark.asyncio
async def test_on_shutdown_polling(tg_bot: TgBot) -> None:
    """
    Tests the on_shutdown method in polling mode.

    :param tg_bot: Instance of TgBot to test.
    :return: None
    """
    tg_bot._broadcaster.broadcast = AsyncMock()
    tg_bot._config.webhook = None
    await tg_bot._on_shutdown()
    tg_bot._broadcaster.broadcast.assert_called_once_with(
        users_ids=tg_bot._config.admins, msg="Bot was stopped", notify=False
    )
    tg_bot._bot.delete_webhook.assert_not_called()
    tg_bot._bot.session.close.assert_called_once()


# noinspection PyUnresolvedReferences,PyPropertyAccess
@pytest.mark.asyncio
async def test_on_shutdown_webhook(tg_bot: TgBot) -> None:
    """
    Tests the on_shutdown method in webhook mode.

    :param tg_bot: Instance of TgBot to test.
    :return: None
    """
    tg_bot._broadcaster.broadcast = AsyncMock()
    tg_bot._bot.delete_webhook = AsyncMock()
    tg_bot._config.webhook = MagicMock()
    await tg_bot._on_shutdown()
    tg_bot._broadcaster.broadcast.assert_called_once_with(
        users_ids=tg_bot._config.admins, msg="Bot was stopped", notify=False
    )
    tg_bot._bot.delete_webhook.assert_called_once()
    tg_bot._bot.session.close.assert_called_once()


# noinspection PyPropertyAccess
def test_run_polling(tg_bot: TgBot, mock_loop: AbstractEventLoop) -> None:
    """
    Tests the run method in polling mode.

    :param tg_bot: Instance of TgBot to test.
    :param mock_loop: Mock event loop.
    :return: None
    """
    with patch(target="bot.MainHandler"), patch.object(target=tg_bot._dp, attribute="startup"), patch.object(
        target=tg_bot._dp, attribute="shutdown"
    ), patch(target="bot.run") as mock_run:
        tg_bot._config.webhook = None
        with patch.object(target=tg_bot._dp, attribute="start_polling", return_value=MagicMock()):
            tg_bot.run()
        assert mock_run.call_count == 1
        assert "main" in mock_run.call_args.kwargs
        tg_bot._dp.startup.register.assert_called_once_with(callback=tg_bot._on_startup)
        tg_bot._dp.shutdown.register.assert_called_once_with(callback=tg_bot._on_shutdown)


# noinspection PyPropertyAccess
@pytest.mark.asyncio
async def test_run_webhook(tg_bot: TgBot, mock_loop: AbstractEventLoop) -> None:
    """
    Tests the run method in webhook mode.

    :param tg_bot: Instance of TgBot to test.
    :param mock_loop: Mock event loop.
    :return: None
    """
    with patch(target="bot.MainHandler"), patch.object(target=tg_bot._dp, attribute="startup"), patch.object(
        target=tg_bot._dp, attribute="shutdown"
    ), patch(target="bot.run_app") as mock_run_app, patch(target="bot.Application") as mock_app, patch(
        target="bot.SimpleRequestHandler"
    ) as mock_handler, patch(
        target="bot.setup_application"
    ) as mock_setup:
        tg_bot._config.webhook = MagicMock()
        tg_bot._config.webhook.wh_path = "webhook_path"
        tg_bot._config.webhook.wh_token = "mock_token"
        tg_bot._config.webhook.app_host = "localhost"
        tg_bot._config.webhook.app_port = 8080
        tg_bot._on_startup = AsyncMock()
        tg_bot._on_shutdown = AsyncMock()
        tg_bot.run()
        await sleep(delay=0.1)
        mock_handler.assert_called_once_with(dispatcher=tg_bot._dp, bot=tg_bot._bot, secret_token="mock_token")
        mock_setup.assert_called_once_with(mock_app.return_value, tg_bot._dp)
        mock_run_app.assert_called_once_with(app=mock_app.return_value, host="localhost", port=8080)
        tg_bot._dp.startup.register.assert_called_once_with(callback=tg_bot._on_startup)
        tg_bot._dp.shutdown.register.assert_called_once_with(callback=tg_bot._on_shutdown)


@pytest.mark.asyncio
async def test_main(mock_loop: AbstractEventLoop) -> None:
    """
    Tests the main function.

    :param mock_loop: Mock event loop.
    :return: None
    """
    with patch(target="bot.TgBot") as mock_tg_bot, patch(target="bot.logger", new_callable=MagicMock) as mock_logger:
        mock_bot_instance: MagicMock = mock_tg_bot.return_value
        mock_bot_instance.run = MagicMock()
        main()
        mock_logger.info.assert_any_call("Starting bot")
        mock_tg_bot.assert_called_once()
        mock_bot_instance.run.assert_called_once()
        mock_logger.info.assert_any_call("Bot stopped!")


@pytest.mark.asyncio
async def test_main_with_exception(mock_loop: AbstractEventLoop) -> None:
    """
    Tests the main function when an exception occurs.

    :param mock_loop: Mock event loop.
    :return: None
    """
    with patch(target="bot.TgBot") as mock_tg_bot, patch(target="bot.logger", new_callable=MagicMock) as mock_logger:
        mock_bot_instance: MagicMock = mock_tg_bot.return_value
        mock_bot_instance.run = MagicMock(side_effect=Exception("Test error"))
        main()
        mock_logger.info.assert_any_call("Starting bot")
        mock_tg_bot.assert_called_once()
        mock_bot_instance.run.assert_called_once()
        mock_logger.critical.assert_called_once_with("Unhandled error: Exception('Test error')")
        mock_logger.info.assert_any_call("Bot stopped!")


@pytest.mark.asyncio
async def test_main_with_keyboard_interrupt(mock_loop: AbstractEventLoop) -> None:
    """
    Tests the main function when a KeyboardInterrupt occurs.

    :param mock_loop: Mock event loop.
    :return: None
    """
    with patch(target="bot.TgBot") as mock_tg_bot, patch(target="bot.logger", new_callable=MagicMock) as mock_logger:
        mock_bot_instance: MagicMock = mock_tg_bot.return_value
        mock_bot_instance.run = MagicMock(side_effect=KeyboardInterrupt)
        main()
        mock_logger.info.assert_any_call("Starting bot")
        mock_tg_bot.assert_called_once()
        mock_bot_instance.run.assert_called_once()
        mock_logger.critical.assert_not_called()
        mock_logger.info.assert_any_call("Bot stopped!")


@pytest.mark.asyncio
async def test_main_with_system_exit(mock_loop: AbstractEventLoop) -> None:
    """
    Tests the main function when a SystemExit occurs.

    :param mock_loop: Mock event loop.
    :return: None
    """
    with patch(target="bot.TgBot") as mock_tg_bot, patch(target="bot.logger", new_callable=MagicMock) as mock_logger:
        mock_bot_instance: MagicMock = mock_tg_bot.return_value
        mock_bot_instance.run = MagicMock(side_effect=SystemExit)
        main()
        mock_logger.info.assert_any_call("Starting bot")
        mock_tg_bot.assert_called_once()
        mock_bot_instance.run.assert_called_once()
        mock_logger.critical.assert_not_called()
        mock_logger.info.assert_any_call("Bot stopped!")

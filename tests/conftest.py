"""Module with fixtures for testing Telegram bot handlers."""

from typing import AsyncIterator, Iterator
from _contextvars import Token

import pytest
import pytest_asyncio
from aiogram import Dispatcher, Bot

from src.tgbot.handlers import register_user_handlers  # pylint: disable=import-error
from tests.utils.fake_data import MockedBot  # pylint: disable=import-error


@pytest_asyncio.fixture()
async def dispatcher() -> AsyncIterator[Dispatcher]:
    """Fixture that provides an instance of aiogram.Dispatcher for testing"""
    dp: Dispatcher = Dispatcher()
    register_user_handlers(router=dp)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest.fixture()
def bot() -> Iterator[MockedBot]:
    """Fixture that provides a mocked instance of aiogram.Bot for testing"""
    test_bot: MockedBot = MockedBot()
    token: Token = Bot.set_current(value=test_bot)
    try:
        yield test_bot
    finally:
        Bot.reset_current(token=token)

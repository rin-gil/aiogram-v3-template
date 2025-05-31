# type: ignore
"""Unit tests for src/tgbot/services/settings.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import AsyncMock, Mock

import pytest
from aiogram import Bot
from aiogram.types import Message
from pytest_mock import MockerFixture

from tgbot.config import Config
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender
from tgbot.services.settings import SettingsService

__all__: tuple = ()


@pytest.fixture
def mock_config(mocker: MockerFixture) -> Config:
    """
    Fixture to provide a mocked Config object.

    :param mocker: Pytest mocker fixture.
    :return: Mocked Config object.
    """
    return mocker.Mock(spec=Config)


@pytest.fixture
def mock_tmpl(mocker: MockerFixture) -> TmplRender:
    """
    Fixture to provide a mocked TmplRender object.

    :param mocker: Pytest mocker fixture.
    :return: Mocked TmplRender object.
    """
    return mocker.Mock(spec=TmplRender)


@pytest.fixture
def mock_kb(mocker: MockerFixture) -> KeyboardManager:
    """
    Fixture to provide a mocked KeyboardManager object.

    :param mocker: Pytest mocker fixture.
    :return: Mocked KeyboardManager object.
    """
    return mocker.Mock(spec=KeyboardManager)


@pytest.fixture
def mock_bot(mocker: MockerFixture) -> Bot:
    """
    Fixture to provide a mocked Bot object.

    :param mocker: Pytest mocker fixture.
    :return: Mocked Bot object.
    """
    bot: Mock = mocker.Mock(spec=Bot)
    bot.get_me = AsyncMock(return_value=mocker.Mock(username="TestBot"))
    return bot


@pytest.fixture
def settings_service(mock_config: Config, mock_tmpl: TmplRender, mock_kb: KeyboardManager) -> SettingsService:
    """
    Fixture to provide an instance of SettingsService with mocked dependencies.

    :param mock_config: Mocked Config object.
    :param mock_tmpl: Mocked TmplRender object.
    :param mock_kb: Mocked KeyboardManager object.
    :return: Instance of SettingsService.
    """
    return SettingsService(config=mock_config, tmpl=mock_tmpl, kb=mock_kb)


@pytest.mark.asyncio
async def test_settings(
    settings_service: SettingsService, mock_tmpl: TmplRender, mock_bot: Bot, mocker: MockerFixture
) -> None:
    """
    Test the settings method to ensure it displays user settings correctly.

    :param settings_service: Instance of SettingsService.
    :param mock_tmpl: Mocked TmplRender object.
    :param mock_bot: Mocked Bot object.
    :param mocker: Pytest mocker fixture.
    """
    # Arrange
    message: Mock = mocker.Mock(spec=Message, from_user=mocker.Mock(id=123, language_code="en"), bot=mock_bot)
    message.answer = AsyncMock()
    mock_tmpl.render = AsyncMock(return_value="Settings text")
    # Act
    await settings_service.settings(message=message)
    # Assert
    # noinspection PyUnresolvedReferences
    mock_tmpl.render.assert_called_once_with(tmpl=settings_service._msg_settings, locale="en")
    message.answer.assert_called_once_with(text="Settings text")

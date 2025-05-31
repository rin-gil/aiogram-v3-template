# type: ignore
"""Unit tests for src/tgbot/handlers/settings.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pytest_mock import MockerFixture

from tgbot.handlers.settings import SettingsHandler
from tgbot.services.settings import SettingsService

__all__: tuple = ()


@pytest.fixture
def mock_service(mocker: MockerFixture) -> SettingsService:
    """
    Fixture to provide a mocked SettingsService object.

    :param mocker: Pytest mocker fixture.
    :return: Mocked SettingsService object.
    """
    return mocker.Mock(spec=SettingsService)


@pytest.fixture
def settings_handler(mock_service: SettingsService) -> SettingsHandler:
    """
    Fixture to provide an instance of SettingsHandler with mocked dependencies.

    :param mock_service: Mocked SettingsService object.
    :return: Instance of SettingsHandler.
    """
    return SettingsHandler(service=mock_service)


@pytest.mark.asyncio
async def test_cmd_or_msg_settings(
    settings_handler: SettingsHandler, mock_service: SettingsService, mocker: MockerFixture
) -> None:
    """
    Test the cmd_or_msg_settings method to ensure it handles settings command correctly.

    :param settings_handler: Instance of SettingsHandler.
    :param mock_service: Mocked SettingsService object.
    :param mocker: Pytest mocker fixture.
    """
    # Arrange
    message: Mock = mocker.Mock(spec=Message)
    message.delete = AsyncMock()
    state: Mock = mocker.Mock(spec=FSMContext)
    state.clear = AsyncMock()
    mock_service.settings = AsyncMock()
    # Act
    await settings_handler.cmd_or_msg_settings(message=message, state=state)
    # Assert
    message.delete.assert_called_once()
    state.clear.assert_called_once()
    mock_service.settings.assert_called_once_with(message=message)

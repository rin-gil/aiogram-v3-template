# type: ignore
"""Unit tests for src/tgbot/handlers/admin.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from tgbot.handlers.admin import AdminHandler
from tgbot.services.admin import AdminService

__all__: tuple = ()


@pytest.fixture
def admin_service_mock() -> AdminService:
    """
    Provide a mocked AdminService instance for testing AdminHandler.

    :return: Mocked AdminService instance
    """
    service: Mock = Mock(spec=AdminService)
    service.admin_menu = AsyncMock()
    return service


@pytest.fixture
def admin_handler_fixture(admin_service_mock: AdminService) -> AdminHandler:
    """
    Provide a fresh AdminHandler instance with mocked AdminService.

    :param admin_service_mock: Mocked AdminService instance
    :return: AdminHandler instance
    """
    return AdminHandler(service=admin_service_mock)


@pytest.fixture
def mock_state() -> FSMContext:
    """
    Fixture to provide a mocked FSMContext instance.

    :return: Mocked FSMContext object
    """
    return FSMContext(storage=MemoryStorage(), key=Mock())


@pytest.mark.asyncio
async def test_cmd_admin(admin_handler_fixture: AdminHandler, mock_state: FSMContext) -> None:
    """
    Test the cmd_admin handler.

    :param admin_handler_fixture: AdminHandler instance with mocked service
    :param mock_state: Mocked FSMContext object
    """
    # Arrange
    message: Mock = Mock(spec=Message)
    message.delete = AsyncMock()
    mock_state.clear = AsyncMock()
    # Act
    await admin_handler_fixture.cmd_admin(message=message, state=mock_state)
    # Assert
    message.delete.assert_called_once()
    mock_state.clear.assert_called_once()
    # noinspection PyUnresolvedReferences
    admin_handler_fixture._service.admin_menu.assert_called_once_with(message=message)

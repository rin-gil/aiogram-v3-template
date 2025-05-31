# type: ignore
"""Unit tests for src/tgbot/handlers/common.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import Message
from pytest_mock import MockerFixture

from tgbot.handlers.common import CommonHandler
from tgbot.services.common import BaseService

__all__: tuple = ()


@pytest.fixture
def mock_service(mocker: MockerFixture) -> BaseService:
    """
    Fixture to provide a mocked BaseService object.

    :param mocker: Pytest mocker fixture.
    :return: Mocked BaseService object.
    """
    return mocker.Mock(spec=BaseService)


@pytest.fixture
def common_handler(mock_service: BaseService) -> CommonHandler:
    """
    Fixture to provide an instance of CommonHandler with mocked dependencies.

    :param mock_service: Mocked BaseService object.
    :return: Instance of CommonHandler.
    """
    return CommonHandler(service=mock_service)


@pytest.mark.asyncio
async def test_any_delete(common_handler: CommonHandler, mock_service: BaseService, mocker: MockerFixture) -> None:
    """
    Test the any_delete method to ensure it deletes user content correctly.

    :param common_handler: Instance of CommonHandler.
    :param mock_service: Mocked BaseService object.
    :param mocker: Pytest mocker fixture.
    """
    # Arrange
    message: Mock = mocker.Mock(spec=Message)
    mock_service.any_delete = AsyncMock()
    # Act
    await common_handler.any_delete(message=message)
    # Assert
    mock_service.any_delete.assert_called_once_with(message=message)

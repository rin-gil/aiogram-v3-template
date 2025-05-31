# type: ignore
"""Unit tests for src/tgbot/services/admin.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import Message, ReplyKeyboardMarkup

from tgbot.config import Config
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender
from tgbot.services.admin import AdminService

__all__: tuple = ()


@pytest.fixture
def mock_config() -> Mock:
    """
    Provide a mocked Config instance.

    :return: Mocked Config instance
    """
    config: Mock = Mock(spec=Config)
    config.admins = [123, 456]
    return config


@pytest.fixture
def mock_tmpl() -> Mock:
    """
    Provide a mocked TmplRender instance.

    :return: Mocked TmplRender instance
    """
    tmpl: Mock = Mock(spec=TmplRender)
    tmpl.render = AsyncMock(return_value="Mocked admin panel text")
    return tmpl


@pytest.fixture
def mock_kb() -> Mock:
    """
    Provide a mocked KeyboardManager instance.

    :return: Mocked KeyboardManager instance
    """
    kb: Mock = Mock(spec=KeyboardManager)
    kb.admin_menu = AsyncMock(return_value=Mock(spec=ReplyKeyboardMarkup))
    return kb


@pytest.fixture
def admin_service(mock_config: Mock, mock_tmpl: Mock, mock_kb: Mock) -> AdminService:
    """
    Provide a fresh AdminService instance with mocked dependencies.

    :param mock_config: Mocked Config instance
    :param mock_tmpl: Mocked TmplRender instance
    :param mock_kb: Mocked KeyboardManager instance
    :return: AdminService instance
    """
    return AdminService(config=mock_config, tmpl=mock_tmpl, kb=mock_kb)


@pytest.mark.asyncio
async def test_admin_menu(admin_service: AdminService, mock_tmpl: Mock) -> None:
    """
    Test the admin_menu method.

    :param admin_service: AdminService instance
    :param mock_tmpl: Mocked TmplRender instance
    :return: None
    """
    # Arrange
    message: Mock = Mock(spec=Message)
    message.from_user = Mock(id=123, language_code="en")
    message.answer = AsyncMock()
    # Act
    await admin_service.admin_menu(message=message)
    # Assert
    mock_tmpl.render.assert_called_once_with(tmpl="admin/msg_admin_panel.jinja2", locale="en")
    message.answer.assert_called_once_with(text="Mocked admin panel text")

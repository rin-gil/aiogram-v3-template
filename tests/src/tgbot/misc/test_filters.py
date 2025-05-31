"""Unit tests for src/tgbot/misc/filters.py"""

# pylint: disable=redefined-outer-name

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from aiogram.types import CallbackQuery, Message, User

from tgbot.config import Config
from tgbot.misc.filters import IsAdmin

__all__: tuple = ()


@pytest.fixture
def mock_user() -> User:
    """
    Fixture to create a mock User object.

    :return: Mock instance of User.
    """
    user: User = MagicMock(spec=User)
    user.id = 12345
    return user


# noinspection PyUnresolvedReferences
@pytest.fixture(params=[CallbackQuery, Message])
def mock_obj(request: pytest.FixtureRequest, mock_user: User) -> CallbackQuery | Message:
    """
    Fixture to create a mock CallbackQuery or Message object.

    :param request: Pytest request object for parameterization.
    :param mock_user: Fixture providing a mock User instance.
    :return: Mock instance of CallbackQuery or Message.
    """
    if request.param is CallbackQuery:
        return MagicMock(spec=CallbackQuery, from_user=mock_user)
    return MagicMock(spec=Message, from_user=mock_user, date=datetime.now(), chat=MagicMock(id=123))


@pytest.fixture
def mock_config() -> Config:
    """
    Fixture to create a mock Config object.

    :return: Mock instance of Config.
    """
    return MagicMock(spec=Config)


@pytest.mark.asyncio
@pytest.mark.parametrize("admins, expected_result", [([12345], True), ([67890], False), ([], False)])
async def test_is_admin(
    mock_obj: CallbackQuery | Message, mock_config: Config, admins: list[int], expected_result: bool
) -> None:
    """
    Test IsAdmin filter with different admin configurations.

    :param mock_obj: Fixture providing a mock CallbackQuery or Message instance.
    :param mock_config: Fixture providing a mock Config instance.
    :param admins: List of admin IDs.
    :param expected_result: Expected result of the filter.
    :return: None
    """
    # noinspection PyPropertyAccess
    mock_config.admins = admins  # type: ignore
    filter_instance: IsAdmin = IsAdmin(admins_ids=mock_config.admins)
    result: bool = await filter_instance(mock_obj)
    assert result == expected_result

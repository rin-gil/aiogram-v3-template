"""Unit tests for src/tgbot/misc/decorators.py"""

# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

from asyncio import CancelledError
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from tgbot.misc.decorators import handle_exc, handle_telegram_exc

__all__: tuple = ()


@pytest.fixture
def mock_self() -> MagicMock:
    """
    Fixture to create a mock self object.

    :return: A mocked self object simulating Broadcaster.
    """
    self_obj: MagicMock = MagicMock()
    return self_obj


@pytest.mark.asyncio
async def test_handle_telegram_exc_no_exception(mock_self: MagicMock) -> None:
    """
    Test handle_telegram_exc decorator when no exception is raised.

    :param mock_self: Fixture providing a mock self object.
    :return: None
    """

    # noinspection PyUnusedLocal
    @handle_telegram_exc
    async def test_func(self: MagicMock) -> int:
        """
        Test function that returns a value without raising an exception.

        :param self: Mocked self object with _db.
        :return: Integer value.
        """
        return 10

    result: int = await test_func(self=mock_self)
    assert result == 10


@pytest.mark.asyncio
async def test_handle_telegram_exc_bad_request(mock_self: MagicMock) -> None:
    """
    Test handle_telegram_exc decorator with TelegramBadRequest exception.

    :param mock_self: Mocked self object with _db.
    :return: None
    """

    # noinspection PyUnusedLocal
    @handle_telegram_exc
    async def test_func(self: MagicMock, user_id: int) -> None:
        """
        Test function that raises TelegramBadRequest.

        :param self: Mocked self object with _db.
        :param user_id: User ID.
        :return: None
        :raises TelegramBadRequest: Simulated TelegramBadRequest exception.
        """
        raise TelegramBadRequest(message="Bad request", method=MagicMock())

    result: int = await test_func(self=mock_self, user_id=123)
    assert result == 0


@pytest.mark.asyncio
async def test_handle_telegram_exc_forbidden_other(mock_self: MagicMock) -> None:
    """
    Test handle_telegram_exc decorator with TelegramForbiddenError for other reasons.

    :param mock_self: Mocked self object with _db.
    :return: None
    """

    # noinspection PyUnusedLocal
    @handle_telegram_exc
    async def test_func(self: MagicMock, user_id: int) -> None:
        """
        Test function that raises TelegramForbiddenError without bot blocked message.

        :param self: Mocked self object with _db.
        :param user_id: User ID.
        :return: None
        :raises TelegramForbiddenError: Simulated TelegramForbiddenError exception.
        """
        raise TelegramForbiddenError(message="Forbidden: other reason", method=MagicMock())

    result: int = await test_func(self=mock_self, user_id=789)
    assert result == 0
    mock_self._db.del_user.assert_not_called()


@pytest.mark.asyncio
@patch(target="tgbot.misc.decorators.sleep", new_callable=AsyncMock)
async def test_handle_telegram_exc_retry_after(mock_sleep: AsyncMock, mock_self: MagicMock) -> None:
    """
    Test handle_telegram_exc decorator with TelegramRetryAfter exception and retry logic.

    :param mock_sleep: A mocked sleep function
    :param mock_self: Mocked self object with _db.
    :return: None
    """
    call_count: int = 0

    # noinspection PyUnusedLocal
    @handle_telegram_exc
    async def test_func(self: MagicMock, user_id: int) -> int:
        """
        Test function that raises TelegramRetryAfter on first call and succeeds on retry.

        :param self: Mocked self object with _db.
        :param user_id: User ID
        :return: Integer value
        :raises TelegramRetryAfter: Simulated TelegramRetryAfter exception
        """
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise TelegramRetryAfter(retry_after=1, method=MagicMock(), message="Flood limit")
        return 10

    result: int = await test_func(self=mock_self, user_id=789)
    assert result == 10
    assert call_count == 2
    mock_sleep.assert_called_once_with(delay=1)


@pytest.mark.asyncio
async def test_handle_telegram_exc_api_error(mock_self: MagicMock) -> None:
    """
    Test handle_telegram_exc decorator with TelegramAPIError exception.

    :param mock_self: Mocked self object with _db.
    :return: None
    """

    # noinspection PyUnusedLocal
    @handle_telegram_exc
    async def test_func(self: MagicMock, user_id: int) -> None:
        """
        Test function that raises TelegramAPIError.

        :param self: Mocked self object with _db.
        :param user_id: User ID
        :return: None
        :raises TelegramAPIError: Simulated TelegramAPIError exception
        """
        raise TelegramAPIError(message="API error", method=MagicMock())

    result: int = await test_func(self=mock_self, user_id=999)
    assert result == 0


@pytest.mark.asyncio
async def test_handle_telegram_exc_no_user_id(mock_self: MagicMock) -> None:
    """
    Test handle_telegram_exc decorator when user_id is not provided.

    :param mock_self: Mocked self object with _db.
    :return: None
    """

    # noinspection PyUnusedLocal
    @handle_telegram_exc
    async def test_func(self: MagicMock) -> None:
        """
        Test function that raises TelegramAPIError without user_id.

        :param self: Mocked self object with _db.
        :return: None
        :raises TelegramAPIError: Simulated TelegramAPIError exception
        """
        raise TelegramAPIError(message="API error", method=MagicMock())

    result: int = await test_func(self=mock_self)
    assert result == 0


@pytest.mark.asyncio
async def test_handle_exc_no_exception() -> None:
    """
    Test handle_exc decorator when no exception is raised.

    :return: None
    """

    @handle_exc
    async def test_func() -> int:
        """
        Test function that returns a value without raising an exception.

        :return: Integer value
        """
        return 20

    result: int = await test_func()
    assert result == 20


@pytest.mark.asyncio
async def test_handle_exc_cancelled_error() -> None:
    """
    Test handle_exc decorator with CancelledError exception.

    :return: None
    """

    @handle_exc
    async def test_func() -> None:
        """
        Test function that raises CancelledError.

        :return: None
        :raises CancelledError: Simulated CancelledError exception
        """
        raise CancelledError("Cancelled")

    result: None = await test_func()
    assert result is None


@pytest.mark.asyncio
async def test_handle_exc_generic_exception() -> None:
    """
    Test handle_exc decorator with a generic exception.

    :return: None
    """

    @handle_exc
    async def test_func() -> None:
        """
        Test function that raises a generic ValueError.

        :return: None
        :raises ValueError: Simulated ValueError exception
        """
        raise ValueError("Generic error")

    result: None = await test_func()
    assert result is None

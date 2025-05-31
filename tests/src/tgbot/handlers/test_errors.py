"""Unit tests for src/tgbot/handlers/errors.py"""

# pylint: disable=redefined-outer-name

from typing import Any
from unittest.mock import Mock, patch

import pytest
from aiogram.handlers import ErrorHandler
from aiogram.types import Update, Message, CallbackQuery, ErrorEvent

from tgbot.handlers.errors import ErrHandler

__all__: tuple = ()


@pytest.fixture
def error_handler() -> ErrHandler:
    """
    Fixture to create a base ErrorHandler instance with a mocked event.

    :return: An instance of ErrHandler with a mocked ErrorEvent.
    """
    event: Mock = Mock(spec=ErrorEvent)
    event.update = Mock(spec=Update)
    return ErrHandler(event=event)


@pytest.mark.asyncio
async def test_handle_with_message(error_handler: ErrHandler) -> None:
    """
    Test handling an error event with a message.

    :param error_handler: The error handler instance to test.
    :return: None
    """
    message: Mock = Mock(spec=Message, text="Test message")
    update: Mock = Mock(spec=Update, message=message, callback_query=None)
    exception: Exception = Exception("Test exception")
    event: Mock = Mock(spec=ErrorEvent, update=update, exception=exception)
    error_handler.event = event
    with patch(target="tgbot.handlers.errors.logger") as mock_logger:
        await error_handler.handle()
        mock_logger.error.assert_called_once_with(
            "Exception while handling an update: Test exception , Message: Test message"
        )


@pytest.mark.asyncio
async def test_handle_with_callback(error_handler: ErrHandler) -> None:
    """
    Test handling an error event with a callback query.

    :param error_handler: The error handler instance to test.
    :return: None
    """
    callback: Mock = Mock(spec=CallbackQuery, data="test_callback")
    update: Mock = Mock(spec=Update, message=None, callback_query=callback)
    exception: Exception = Exception("Test exception")
    event: Mock = Mock(spec=ErrorEvent, update=update, exception=exception)
    error_handler.event = event
    with patch(target="tgbot.handlers.errors.logger") as mock_logger:
        await error_handler.handle()
        mock_logger.error.assert_called_once_with(
            "Exception while handling an update: Test exception , Callback: test_callback"
        )


@pytest.mark.asyncio
async def test_handle_without_message_or_callback(error_handler: ErrHandler) -> None:
    """
    Test handling an error event without a message or callback query.

    :param error_handler: The error handler instance to test.
    :return: None
    """
    update: Mock = Mock(spec=Update, message=None, callback_query=None)
    exception: Exception = Exception("Test exception")
    event: Mock = Mock(spec=ErrorEvent, update=update, exception=exception)
    error_handler.event = event
    with patch(target="tgbot.handlers.errors.logger") as mock_logger:
        await error_handler.handle()
        mock_logger.error.assert_called_once_with("Exception while handling an update: Test exception ")


def test_error_handler_init(error_handler: ErrHandler) -> None:
    """
    Test the basic initialization of the error handler.

    :param error_handler: The error handler instance to test.
    :return: None
    """
    assert isinstance(error_handler, ErrorHandler)
    assert hasattr(error_handler, "event")
    assert hasattr(error_handler, "handle")


@pytest.mark.asyncio
async def test_handle_with_broken_event(error_handler: ErrHandler) -> None:
    """
    Test handling an error event with minimal attributes.

    :param error_handler: The error handler instance to test.
    :return: None
    """
    update: Mock = Mock(spec=Update, message=None, callback_query=None)
    event: Mock = Mock(spec=ErrorEvent, update=update, exception=Exception("Test exception"))
    error_handler.event = event
    with patch(target="tgbot.handlers.errors.logger") as mock_logger:
        await error_handler.handle()
        mock_logger.error.assert_called_once()
        call_args: Any = mock_logger.error.call_args[0][0]
        assert "Test exception" in call_args

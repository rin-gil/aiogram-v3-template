"""The module implements the decorators used in the application."""

import sys
from asyncio import CancelledError, sleep
from functools import wraps
from traceback import format_exc
from typing import Any, Callable

from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from tgbot.config import logger

__all__: tuple[str, ...] = ("handle_exc", "handle_telegram_exc")


def handle_telegram_exc(func: Callable) -> Callable:
    """
    Async decorator to handle Telegram API exceptions.

    :param func: The asynchronous function to wrap.
    :return: The wrapped asynchronous function.
    """

    @wraps(wrapped=func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper function to catch and handle exceptions during the execution of the wrapped function

        :param args: Positional arguments for the wrapped function.
        :param kwargs: Keyword arguments for the wrapped function.
        :return: The result of the wrapped function (message ID) or 0 in case of an exception.
        """
        try:
            return await func(*args, **kwargs)
        except TelegramForbiddenError as exc:
            logger.error(f"Target [ID:{kwargs.get('user_id')}]: failed with error {exc}")
        except TelegramBadRequest as exc:
            logger.error(f"Target [ID:{kwargs.get('user_id')}]: failed with error {exc}")
        except TelegramRetryAfter as exc:
            logger.warning(f"Target [ID:{kwargs.get('user_id')}]: Flood limit, sleep {exc.retry_after} sec.")
            await sleep(delay=exc.retry_after)
            return await wrapper(*args, **kwargs)
        except TelegramAPIError as exc:
            logger.error(f"Target [ID:{kwargs.get('user_id')}]: failed with error {exc}")
        return 0

    return wrapper


def handle_exc(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that catches exceptions in an async function.

    :param func: The asynchronous function to decorate.
    :return: The decorated function with error handling.
    """

    @wraps(wrapped=func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wraps the decorated async function and handles exceptions

        :param args: positional arguments passed to the wrapped function
        :param kwargs: keyword arguments passed to the wrapped function
        :return: the result of the wrapped async function
        """
        try:
            return await func(*args, **kwargs)
        except CancelledError:
            pass
        except Exception as exc:
            tb: str = f"\n{format_exc()}" if not hasattr(sys, "tracebacklimit") else ""
            logger.error(f"Task '{func.__name__}' caused an exception: {exc}{tb}")

    return wrapper

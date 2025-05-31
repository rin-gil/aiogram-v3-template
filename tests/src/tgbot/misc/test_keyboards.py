"""Unit tests for src/tgbot/misc/keyboards.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import MagicMock

import pytest

from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender

__all__: tuple = ()


@pytest.fixture
def mock_tmpl_render() -> TmplRender:
    """
    Provides a mocked TmplRender instance for testing.

    :return: A mocked TmplRender instance.
    """
    return MagicMock(spec=TmplRender)


def test_init(mock_tmpl_render: TmplRender) -> None:
    """
    Tests the __init__ method of KeyboardManager.

    :param mock_tmpl_render: The mocked TmplRender instance provided by fixture.
    :return: None
    """
    keyboard_manager: KeyboardManager = KeyboardManager(tmpl=mock_tmpl_render)
    assert keyboard_manager._tmpl is mock_tmpl_render

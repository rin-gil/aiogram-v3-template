# type: ignore
"""Unit tests for src/tgbot/services/common.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import EditMessageText
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, User
from pytest_mock import MockerFixture

from tgbot.config import Config
from tgbot.misc.keyboards import KeyboardManager
from tgbot.misc.tmpl_render import TmplRender
from tgbot.services.common import BaseService

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
def base_service(mock_config: Config, mock_tmpl: TmplRender, mock_kb: KeyboardManager) -> BaseService:
    """
    Fixture to provide an instance of BaseService with mocked dependencies.

    :param mock_config: Mocked Config object.
    :param mock_tmpl: Mocked TmplRender object.
    :param mock_kb: Mocked KeyboardManager object.
    :return: Instance of BaseService.
    """
    return BaseService(config=mock_config, tmpl=mock_tmpl, kb=mock_kb)


@pytest.fixture
def callback_query(mocker: MockerFixture) -> CallbackQuery:
    """
    Fixture to provide a mocked CallbackQuery object with a message attribute.

    :param mocker: Pytest mocker fixture.
    :return: Mocked CallbackQuery object.
    """
    call: Mock = mocker.Mock(spec=CallbackQuery)
    call.from_user = mocker.Mock(spec=User, language_code="en")
    call.message = mocker.Mock(spec=Message)
    return call


@pytest.fixture
def message(mocker: MockerFixture) -> Message:
    """
    Fixture to provide a mocked Message object.

    :param mocker: Pytest mocker fixture.
    :return: Mocked Message object.
    """
    msg: Mock = mocker.Mock(spec=Message)
    msg.from_user = mocker.Mock(spec=User, language_code="en")
    return msg


@pytest.mark.asyncio
async def test_any_delete(
    base_service: BaseService, mock_tmpl: TmplRender, message: Message, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test the any_delete method to ensure it deletes unsupported user content correctly.

    :param base_service: Instance of BaseService.
    :param mock_tmpl: Mocked TmplRender object.
    :param message: Mocked Message object.
    :param monkeypatch: Pytest monkeypatch fixture for patching module attributes.
    """
    # Arrange
    reply_msg: Mock = Mock(spec=Message)
    message.reply = AsyncMock(return_value=reply_msg)
    reply_msg.delete = AsyncMock()
    message.delete = AsyncMock()
    mock_tmpl.render = AsyncMock(return_value="Unsupported text")
    sleep_mock: AsyncMock = AsyncMock()
    monkeypatch.setattr(target="tgbot.services.common.sleep", name=sleep_mock)
    # Act
    await base_service.any_delete(message=message)
    # Assert
    mock_tmpl.render.assert_called_once_with(tmpl=base_service._msg_unsupported, locale="en")
    message.reply.assert_called_once_with(text="Unsupported text")
    reply_msg.delete.assert_called_once()
    message.delete.assert_called_once()
    sleep_mock.assert_called_once_with(delay=3)


@pytest.mark.asyncio
async def test_edit_or_send_callback_success(base_service: BaseService, callback_query: CallbackQuery) -> None:
    """
    Test the _edit_or_send_callback method when editing succeeds.

    :param base_service: Instance of BaseService.
    :param callback_query: Mocked CallbackQuery object.
    """
    # Arrange
    callback_query.message.edit_text = AsyncMock(return_value=Mock(spec=Message))
    callback_query.answer = AsyncMock()
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[])
    text: str = "Edited text"
    # Act
    result: Message = await base_service._edit_or_send_callback(
        call=callback_query, text=text, reply_markup=reply_markup
    )
    # Assert
    callback_query.message.edit_text.assert_called_once_with(text=text, reply_markup=reply_markup)
    callback_query.answer.assert_called_once_with()
    assert result == callback_query.message.edit_text.return_value


@pytest.mark.asyncio
async def test_edit_or_send_callback_failure(
    base_service: BaseService, mock_tmpl: TmplRender, callback_query: CallbackQuery
) -> None:
    """
    Test the _edit_or_send_callback method when editing fails due to TelegramBadRequest.

    :param base_service: Instance of BaseService.
    :param mock_tmpl: Mocked TmplRender object.
    :param callback_query: Mocked CallbackQuery object.
    """
    # Arrange
    callback_query.message.edit_text = AsyncMock(
        side_effect=TelegramBadRequest(method=EditMessageText(text="Test"), message="Too old")
    )
    callback_query.message.answer = AsyncMock(return_value=Mock(spec=Message))
    callback_query.answer = AsyncMock()
    mock_tmpl.render = AsyncMock(return_value="Expired action text")
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[])
    text: str = "New text"
    # Act
    result: Message = await base_service._edit_or_send_callback(
        call=callback_query, text=text, reply_markup=reply_markup
    )
    # Assert
    callback_query.message.edit_text.assert_called_once_with(text=text, reply_markup=reply_markup)
    mock_tmpl.render.assert_called_once_with(tmpl=base_service._msg_expired_action, locale="en")
    callback_query.answer.assert_called_once_with(text="Expired action text", show_alert=True)
    callback_query.message.answer.assert_called_once_with(text=text, reply_markup=reply_markup)
    assert result == callback_query.message.answer.return_value


# noinspection PyUnresolvedReferences
@pytest.mark.asyncio
async def test_edit_or_send_callback_same_content(
    base_service: BaseService, callback_query: CallbackQuery, mocker: MockerFixture
) -> None:
    """
    Test the _edit_or_send_callback method when editing fails due to same content.

    :param base_service: Instance of BaseService.
    :param callback_query: Mocked CallbackQuery object.
    :param mocker: Pytest mocker fixture.
    """
    # Arrange
    # noinspection PyTypeChecker
    mocker.patch.object(
        target=callback_query.message,
        attribute="edit_text",
        side_effect=TelegramBadRequest(method="editMessageText", message="the same as a current content"),
    )
    callback_query.answer = AsyncMock()
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[])
    text: str = "Same text"
    # Act
    result: Message = await base_service._edit_or_send_callback(
        call=callback_query, text=text, reply_markup=reply_markup
    )
    # Assert
    callback_query.message.edit_text.assert_called_once_with(text=text, reply_markup=reply_markup)
    callback_query.answer.assert_called_once_with()
    callback_query.message.answer.assert_not_called()
    assert result == callback_query.message


@pytest.mark.asyncio
async def test_edit_or_send_msg_success(base_service: BaseService, message: Message) -> None:
    """
    Test the _edit_or_send_msg method when editing succeeds.

    :param base_service: Instance of BaseService.
    :param message: Mocked Message object.
    """
    # Arrange
    # noinspection PyPropertyAccess
    message.bot = AsyncMock()
    message.bot.edit_message_text = AsyncMock(return_value=Mock(spec=Message))
    message.chat = Mock(id=12345)
    message.message_id = 67890
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[])
    text: str = "Edited text"
    # Act
    result: Message = await base_service._edit_or_send_msg(
        bot=message.bot, chat_id=message.chat.id, msg_id=message.message_id, text=text, reply_markup=reply_markup
    )
    # Assert
    message.bot.edit_message_text.assert_called_once_with(
        chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=reply_markup
    )
    # noinspection PyUnresolvedReferences
    message.bot.send_message.assert_not_called()
    assert result == message.bot.edit_message_text.return_value


@pytest.mark.asyncio
async def test_edit_or_send_msg_failure(base_service: BaseService, message: Message) -> None:
    """
    Test the _edit_or_send_msg method when editing fails due to TelegramBadRequest.

    :param base_service: Instance of BaseService.
    :param message: Mocked Message object.
    """
    # Arrange
    # noinspection PyPropertyAccess
    message.bot = AsyncMock()
    message.bot.edit_message_text = AsyncMock(
        side_effect=TelegramBadRequest(method=EditMessageText(text="Test"), message="Too old")
    )
    message.bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    message.chat = Mock(id=12345)
    message.message_id = 67890
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[])
    text: str = "New text"
    # Act
    result: Message = await base_service._edit_or_send_msg(
        bot=message.bot, chat_id=message.chat.id, msg_id=message.message_id, text=text, reply_markup=reply_markup
    )
    # Assert
    message.bot.edit_message_text.assert_called_once_with(
        chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=reply_markup
    )
    message.bot.send_message.assert_called_once_with(chat_id=message.chat.id, text=text, reply_markup=reply_markup)
    assert result == message.bot.send_message.return_value

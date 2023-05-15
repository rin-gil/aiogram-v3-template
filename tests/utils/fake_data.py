"""The module contains fake data and functions for testing the bot"""

from collections import deque
from datetime import datetime
from typing import Any, AsyncGenerator, Deque, Optional, Type, TYPE_CHECKING

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.methods.base import Request, Response, TelegramType
from aiogram.types import CallbackQuery, Chat, Message, Update
from aiogram.types import UNSET, User, ResponseParameters


TEST_USER: User = User(id=123456789, is_bot=False, first_name="Test", username="test_user")
TEST_USER_CHAT: Chat = Chat(id=123456789, type="private", username=TEST_USER.username, first_name=TEST_USER.first_name)


class MockedSession(BaseSession):
    """Implements a simulated session to test the bot"""

    def __init__(self) -> None:
        super().__init__()
        self.responses: Deque[Response[TelegramType]] = deque()  # type: ignore
        self.requests: Deque[Request] = deque()
        self.closed = True

    def add_result(self, response: Response[TelegramType]) -> Response[TelegramType]:
        """Adds the Response object to the response queue"""
        self.responses.append(response)
        return response

    def get_request(self) -> Request:
        """Retrieves and returns the Request object from the request queue"""
        return self.requests.pop()

    async def close(self) -> None:
        self.closed = True

    async def make_request(
        self, bot: Bot, method: TelegramMethod[TelegramType], timeout: Optional[int] = UNSET
    ) -> TelegramType:
        return method  # type: ignore

    async def stream_content(
        self, url: str, timeout: int, chunk_size: int, raise_for_status: bool
    ) -> AsyncGenerator[bytes, None]:
        yield b""


class MockedBot(Bot):
    """Implements a simulated bot for tests"""

    if TYPE_CHECKING:
        session: MockedSession

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(kwargs.pop("token", "42:TEST"), session=MockedSession(), **kwargs)
        self._me = User(
            id=self.id, is_bot=True, first_name="Test", last_name="Bot", username="test_bot", language_code="en"
        )

    def add_result_for(
        self,
        method: Type[TelegramMethod[TelegramType]],
        ok: bool,
        result: TelegramType = None,
        description: Optional[str] = None,
        error_code: int = 200,
        migrate_to_chat_id: Optional[int] = None,
        retry_after: Optional[int] = None,
    ) -> Response[TelegramType]:
        """Adds the query result to the session"""
        response = Response[method.__returning__](  # type: ignore
            ok=ok,
            result=result,
            description=description,
            error_code=error_code,
            parameters=ResponseParameters(migrate_to_chat_id=migrate_to_chat_id, retry_after=retry_after),
        )
        self.session.add_result(response)
        return response

    def get_request(self) -> Request:
        """Retrieves and returns the Request object from the session"""
        return self.session.get_request()


def get_message(text: str, from_user: User = TEST_USER, chat: Chat = TEST_USER_CHAT) -> Message:
    """Returns Message object with the specified text"""
    return Message(message_id=987654321, date=datetime.now(), chat=chat, from_user=from_user, text=text)  # type: ignore


def get_callback_query(data: str | None) -> CallbackQuery:
    """Returns Message object with the specified data"""
    return CallbackQuery(  # type: ignore
        id="test", from_user=TEST_USER, chat_instance="test", message=get_message("test"), data=data
    )


def get_update(message: Message = None, callback_query: CallbackQuery = None) -> Update:
    """Returns CallbackQuery object with the specified Message or CallbackQuery"""
    return Update(update_id=123456789, message=message, callback_query=callback_query)

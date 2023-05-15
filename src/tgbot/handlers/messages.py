"""
This module contains handlers that handle messages from users

Handlers:
    echo    - echoes the user's message
"""

from aiogram.types import Message


async def echo(message: Message) -> Message:
    """Responds to echoing messages"""
    return await message.reply(text=f"<pre>{message.text}</pre>")

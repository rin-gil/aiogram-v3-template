"""
The module contains handlers that respond to commands from bot users

Contains:
    start_cmd_from_admin    - response to the '/start' command from the bot administrators
    start_cmd_from_user     - response to the '/start' command from the bot users
    help_cmd                - response to the '/help' command
"""

from aiogram.types import FSInputFile, Message

from tgbot.config import BotConfig


async def start_cmd_from_admin(message: Message) -> Message:
    """This handler receive messages with `/start` command from bot admins"""
    return await message.answer(text="👋 Hello, admin!")


async def start_cmd_from_user(message: Message) -> Message:
    """This handler receive messages with `/start` command from bot users"""
    username: str = message.from_user.first_name
    return await message.answer(text=f"👋 Hello, {username if username else 'user'}!")


async def help_cmd(message: Message, config: BotConfig) -> Message:
    """This handler receive messages with `/help` command"""
    caption: str = (
        "This is a template for a telegram bot written in Python using the "
        "<b><a href='https://github.com/aiogram/aiogram'>aiogram</a></b> framework"
        "\n\n"
        "The source code of the template is"
        " available in the repository on <b><a href='https://github.com/rin-gil/aiogram-v3-template'>GitHub</a></b>"
    )
    return await message.answer_photo(photo=FSInputFile(path=config.paths.logo_path), caption=caption)

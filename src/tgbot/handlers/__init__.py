"""
The module contains event handlers in the bot.

Modules:
    callbacks.py    - handlers for user button presses
    commands.py     - handlers for user commands
    messages.py     - handlers for user messages
    errors.py       - handlers for errors
"""

from aiogram import F
from aiogram import Router
from aiogram.filters import Command

from tgbot.handlers.commands import help_cmd, start_cmd_from_admin, start_cmd_from_user
from tgbot.handlers.errors import error_handler
from tgbot.handlers.messages import echo
from tgbot.misc.filters import IsAdmin


__all__: tuple[str] = ("register_user_handlers",)


def register_user_commands(router: Router) -> None:
    """Registers user handlers"""

    router.message.register(start_cmd_from_admin, *(Command(commands=["start"]), IsAdmin()))
    router.message.register(start_cmd_from_user, Command(commands=["start"]))
    router.message.register(help_cmd, Command(commands=["help"]))
    router.message.register(echo, F.text)
    router.errors.register(error_handler)


# Alias
register_user_handlers = register_user_commands

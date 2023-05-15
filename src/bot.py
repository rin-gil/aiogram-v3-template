"""Launches the bot"""

from asyncio import run

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.config import BotConfig, ENV_FILE, logger
from tgbot.handlers import register_user_handlers

from tgbot.misc.bot_commands import set_default_commands
from tgbot.services.broadcaster import broadcast


async def on_startup(bot: Bot, config: BotConfig) -> None:
    """The functions that runs when the bot starts, before the dp.start_polling()"""
    await set_default_commands(bot=bot)
    await broadcast(bot=bot, users=config.admin_ids, msg="Bot was started", disable_notification=True)


async def on_shutdown(bot: Bot, config: BotConfig) -> None:
    """The functions that runs when the bot is stopped"""
    await broadcast(bot=bot, users=config.admin_ids, msg="Bot was stopped", disable_notification=True)


async def start_bot() -> None:
    """Launches the bot"""
    config: BotConfig = BotConfig(path_to_env_file=ENV_FILE)
    bot: Bot = Bot(token=config.token, parse_mode="HTML")
    dp: Dispatcher = Dispatcher(storage=MemoryStorage())
    register_user_handlers(router=dp)
    dp.startup.register(callback=on_startup)
    dp.shutdown.register(callback=on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, config=config)


if __name__ == "__main__":
    try:
        logger.info("Starting bot")
        run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as exc:
        logger.critical("Unhandled error: %s", repr(exc))
    finally:
        logger.info("Bot stopped!")

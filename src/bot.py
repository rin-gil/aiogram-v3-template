"""Launches the bot"""

from asyncio import run

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web import run_app
from aiohttp.web_app import Application

from tgbot.config import BotConfig, logger
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
    if config.webhook:
        await bot.delete_webhook()
        await bot.session.close()


def start_bot() -> None:
    """Runs the bot"""
    config: BotConfig = BotConfig()
    bot: Bot = Bot(token=config.token, parse_mode="HTML")
    storage: MemoryStorage | RedisStorage = (
        RedisStorage.from_url(url=config.redis_dsn, key_builder=DefaultKeyBuilder(prefix="tgbot_fsm"))
        if config.redis_dsn
        else MemoryStorage()
    )
    dp: Dispatcher = Dispatcher(storage=storage)
    register_user_handlers(router=dp)
    dp.startup.register(callback=on_startup)
    dp.shutdown.register(callback=on_shutdown)

    if config.webhook:
        app = Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=config.webhook.wh_token, config=config).register(
            app, path=f"/{config.webhook.wh_path}"
        )
        setup_application(app, dp, bot=bot, config=config)

        run_app(app, host=config.webhook.app_host, port=config.webhook.app_port)

    else:
        run(dp.start_polling(bot, config=config))


if __name__ == "__main__":
    try:
        logger.info("Starting bot")
        start_bot()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as exc:
        logger.critical("Unhandled error: %s", repr(exc))
    finally:
        logger.info("Bot stopped!")

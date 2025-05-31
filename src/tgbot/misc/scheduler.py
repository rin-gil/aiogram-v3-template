"""The module allows running tasks on a schedule."""

from datetime import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.misc.broadcaster import Broadcaster
from tgbot.misc.tmpl_render import TmplRender

__all__: tuple[str] = ("Scheduler",)


class Scheduler:
    """Allows to run tasks on a schedule."""

    def __init__(self, config: Config, broadcaster: Broadcaster, tmpl: TmplRender) -> None:
        """
        Initialize the necessary parameters.

        :param config: Config object with configuration parameters.
        :param broadcaster: Broadcaster object for broadcasting messages.
        :param tmpl: TmplRender object for rendering templates.
        """
        self._scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=timezone.utc)
        self._config: Config = config
        self._broadcaster: Broadcaster = broadcaster
        self._tmpl: TmplRender = tmpl

    async def schedule(self) -> None:
        """
        Creates a tasks in the scheduler

        :return: None
        """
        # Start scheduler
        self._scheduler.start()

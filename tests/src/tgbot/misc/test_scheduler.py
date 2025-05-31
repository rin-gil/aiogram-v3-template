"""Unit tests for src/tgbot/misc/scheduler.py"""

# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

from datetime import timezone
from unittest.mock import MagicMock, patch

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.misc.broadcaster import Broadcaster
from tgbot.misc.scheduler import Scheduler
from tgbot.misc.tmpl_render import TmplRender

__all__: tuple = ()


@pytest.fixture
def scheduler() -> Scheduler:
    """
    Provide a fresh Scheduler instance for each test.

    :return: Scheduler instance.
    """
    config: Config = MagicMock(spec=Config)
    broadcaster: Broadcaster = MagicMock(spec=Broadcaster)
    tmpl: TmplRender = MagicMock(spec=TmplRender)
    scheduler: Scheduler = Scheduler(config=config, broadcaster=broadcaster, tmpl=tmpl)
    return scheduler


def test_init(scheduler: Scheduler) -> None:
    """
    Test initialization of Scheduler.

    :param scheduler: Instance of Scheduler to test.
    :return: None
    """
    assert isinstance(scheduler._scheduler, AsyncIOScheduler)
    assert scheduler._scheduler.timezone == timezone.utc
    assert isinstance(scheduler._config, Config)
    assert isinstance(scheduler._broadcaster, Broadcaster)
    assert isinstance(scheduler._tmpl, TmplRender)


@pytest.mark.asyncio
async def test_schedule(scheduler: Scheduler) -> None:
    """
    Test scheduling of all tasks.

    :param scheduler: Instance of Scheduler to test.
    :return: None
    """
    with patch.object(target=scheduler._scheduler, attribute="add_job") as mock_add_job, patch.object(
        target=scheduler._scheduler, attribute="start"
    ) as mock_start:
        # Execute the method
        await scheduler.schedule()
        # Verify calls
        assert mock_add_job.call_count == 0  # no tasks added
        mock_start.assert_called_once()

"""Unit tests for src/tgbot/config.py"""

# pylint: disable=redefined-outer-name

import os
import sys
from pathlib import Path
from typing import Any, Generator

import pytest
from environs import EnvError
from redis.asyncio import Redis

from tgbot.config import Config, logger
from tgbot.misc.dataclasses import Paths, WebhookCredentials

__all__: tuple = ()

ENV_FILE_CONTENT: str = """
    BOT_TOKEN=testtoken
    ADMIN_IDS=123,456
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_DB_INDEX=0
    REDIS_DB_PASS=testpass
    REDIS_DB_USER=testuser_redis
    REDIS_SOCKET_PATH=/var/run/redis/redis-server.sock
    WEBHOOK_HOST=webhookhost
    WEBHOOK_PATH=webhookpath
    WEBHOOK_TOKEN=webhooktoken
    WEBAPP_HOST=apphost
    WEBAPP_PORT=8080
"""


# region Fixtures
@pytest.fixture
def env_file_path(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Fixture to create a .env file one level above the base_dir (tmp_path).

    :param tmp_path: Temporary directory provided by pytest (represents base_dir).
    :return: Path to the created .env file.
    """
    env_p = tmp_path.parent / ".env"
    env_p.parent.mkdir(parents=True, exist_ok=True)
    env_p.write_text(data=ENV_FILE_CONTENT, encoding="utf-8")
    yield env_p
    if env_p.exists():
        env_p.unlink()


@pytest.fixture
def config_instance(tmp_path: Path, env_file_path: Path) -> Config:
    """
    Fixture to create a Config instance with a populated .env file.

    :param tmp_path: Temporary directory provided by pytest.
    :param env_file_path: Fixture ensuring the .env file exists.
    :return: Config instance with loaded environment variables.
    """
    return Config(base_dir=tmp_path)


@pytest.fixture(autouse=True)
def clear_env() -> Generator[None, None, None]:
    """
    Fixture to clear relevant environment variables before each test.

    :return: None
    """
    env_keys_to_clear: list[str] = [
        "BOT_TOKEN",
        "ADMIN_IDS",
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_DB_INDEX",
        "REDIS_DB_PASS",
        "REDIS_DB_USER",
        "REDIS_SOCKET_PATH",
        "WEBHOOK_HOST",
        "WEBHOOK_PATH",
        "WEBHOOK_TOKEN",
        "WEBAPP_HOST",
        "WEBAPP_PORT",
    ]
    original_values: dict[str, str | None] = {key: os.environ.get(key) for key in env_keys_to_clear}
    for key in env_keys_to_clear:
        if key in os.environ:
            del os.environ[key]
    yield
    # Restore original values
    for key, value in original_values.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            # If the key was added during the test but wasn't there originally
            del os.environ[key]


# endregion


# region Tests for Logging
def test_logger_type() -> None:
    """
    Test that logger is initialized as a Logger instance.

    :return: None
    """
    assert isinstance(logger, type(logger))


def test_logger_output_to_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that logger outputs messages to stderr.

    :param capsys: Fixture to capture output.
    :return: None
    """
    logger.remove()
    logger.add(sink=sys.stderr, level="INFO")
    logger.info("Test message to stderr")
    captured = capsys.readouterr()
    assert "Test message to stderr" in captured.err


def test_logger_output_to_file(tmp_path: Path) -> None:
    """
    Test that logger outputs messages to a file.

    :param tmp_path: Temporary directory provided by pytest.
    :return: None
    """
    log_file: Path = Path(tmp_path, "logs/tgbot.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(sink=log_file, level="INFO")
    logger.error("Test message to file")
    assert log_file.exists()
    with log_file.open(mode="r", encoding="utf-8") as file:
        content: str = file.read()
    assert "Test message to file" in content


# endregion


# region Tests for Config
@pytest.mark.parametrize("debug, exp_tb_limit", [(True, 1000), (False, 0)])  # sys.tracebacklimit default is 1000
def test_config_tracebacklimit(debug: bool, exp_tb_limit: int, tmp_path: Path, env_file_path: Path) -> None:
    """
    Test that Config sets sys.tracebacklimit based on the debug flag passed to __init__.

    :param debug: Debug mode flag to pass to Config.
    :param exp_tb_limit: Expected tracebacklimit value.
    :param tmp_path: Temporary directory provided by pytest.
    :param env_file_path: Fixture ensuring the .env file exists.
    :return: None
    """
    original_limit: int = getattr(sys, "tracebacklimit", 1000)
    try:
        Config(base_dir=tmp_path, debug=debug)
        assert getattr(sys, "tracebacklimit", 1000) == exp_tb_limit
    finally:
        sys.tracebacklimit = original_limit


def test_config_init_no_env_file(tmp_path: Path) -> None:
    """
    Test that Config raises FileNotFoundError when .env file is missing.

    :param tmp_path: Temporary directory provided by pytest (used as base_dir).
    :return: None
    """
    env_p: Path = Path(tmp_path.parent, ".env")
    if env_p.exists():
        env_p.unlink()
    with pytest.raises(expected_exception=FileNotFoundError, match="The .env file was not found"):
        Config(base_dir=tmp_path)


def test_config_reads_env_variables(config_instance: Config) -> None:
    """
    Test that Config reads environment variables correctly using the fixture.

    :param config_instance: Fixture providing a Config instance.
    :return: None
    """
    assert config_instance.token == "testtoken"
    assert config_instance.admins == [123, 456]


def test_config_paths(config_instance: Config, tmp_path: Path) -> None:
    """
    Test that Config initializes file paths correctly relative to base_dir.

    :param config_instance: Fixture providing a Config instance.
    :param tmp_path: Temporary directory (used as base_dir in the fixture).
    :return: None
    """
    expected_locale: Path = Path(tmp_path, "locales")
    expected_logo: Path = Path(tmp_path, "assets/img/bot_logo.jpg")
    expected_temp: Path = Path(tmp_path, "temp")
    expected_tmpl: Path = Path(tmp_path, "templates")
    assert isinstance(config_instance.paths, Paths)
    assert config_instance.paths.locale == expected_locale
    assert config_instance.paths.bot_logo == expected_logo
    assert config_instance.paths.temp == expected_temp
    assert config_instance.paths.tmpl == expected_tmpl
    assert expected_locale.exists()
    assert expected_temp.exists()
    assert expected_tmpl.exists()


@pytest.mark.parametrize(
    "use_redis, use_redis_socket, expect_redis",
    [(False, False, False), (True, False, True), (True, True, True), (False, True, False)],
)
def test_config_redis(
    use_redis: bool, use_redis_socket: bool, expect_redis: bool, tmp_path: Path, env_file_path: Path
) -> None:
    """
    Test that Config initializes redis correctly based on constructor flags.

    :param use_redis: Flag to enable/disable redis usage.
    :param use_redis_socket: Flag to enable/disable redis socket.
    :param expect_redis: Whether redis should be initialized (True) or not (False).
    :param tmp_path: Temporary directory provided by pytest.
    :param env_file_path: Fixture ensuring the .env file exists.
    :return: None
    """
    config: Config = Config(base_dir=tmp_path, use_redis=use_redis, use_redis_socket=use_redis_socket)
    if expect_redis:
        assert isinstance(config.redis, Redis)
        conn_kwargs: dict[str, Any] = config.redis.connection_pool.connection_kwargs
        if use_redis_socket:
            assert conn_kwargs.get("path") == "/var/run/redis/redis-server.sock"
            assert conn_kwargs.get("host") is None
            assert conn_kwargs.get("port") is None
        else:
            assert conn_kwargs.get("host") == "localhost"
            assert conn_kwargs.get("port") == 6379
            assert conn_kwargs.get("path") is None
        assert conn_kwargs.get("db") == 0
        assert conn_kwargs.get("password") == "testpass"
        assert conn_kwargs.get("username") == "testuser_redis"
    else:
        assert config.redis is None


@pytest.mark.parametrize("use_webhook, expect_webhook", [(False, False), (True, True)])
def test_config_webhook(use_webhook: bool, expect_webhook: bool, tmp_path: Path, env_file_path: Path) -> None:
    """
    Test that Config initializes webhook correctly based on the constructor flag.

    :param use_webhook: Flag to enable/disable webhook usage.
    :param expect_webhook: Whether webhook should be initialized (True) or not (False).
    :param tmp_path: Temporary directory provided by pytest.
    :param env_file_path: Fixture ensuring the .env file exists.
    :return: None
    """
    config: Config = Config(base_dir=tmp_path, use_webhook=use_webhook)
    if expect_webhook:
        assert isinstance(config.webhook, WebhookCredentials)
        assert config.webhook.wh_host == "webhookhost"
        assert config.webhook.wh_path == "webhookpath"
        assert config.webhook.wh_token == "webhooktoken"
        assert config.webhook.app_host == "apphost"
        assert config.webhook.app_port == 8080
    else:
        assert config.webhook is None


# endregion


# region Tests for errors EnvError
def _create_modified_env(tmp_path: Path, vars_to_remove: list[str]) -> None:
    """
    Helper function to create a modified .env file.

    :param tmp_path: Temporary directory provided by pytest.
    :param vars_to_remove: List of variables to remove from the .env file.
    :return: None
    """
    content_lines: list[str] = ENV_FILE_CONTENT.splitlines()
    modified_content: str = "\n".join(line for line in content_lines if not any(var in line for var in vars_to_remove))
    env_p: Path = Path(tmp_path.parent, ".env")
    env_p.parent.mkdir(parents=True, exist_ok=True)
    env_p.write_text(data=modified_content, encoding="utf-8")


@pytest.mark.parametrize(
    "env_vars_to_remove, error_message_match",
    [
        (["ADMIN_IDS"], "Admin IDs not found"),
        (["BOT_TOKEN"], "BOT_TOKEN not found"),
        (["REDIS_HOST"], "Redis credentials not found"),
        (["WEBHOOK_HOST"], "Webhook credentials not found"),
    ],
)
def test_config_missing_env_var(tmp_path: Path, env_vars_to_remove: list[str], error_message_match: str) -> None:
    """
    Test that Config raises EnvError when essential environment variables are missing.

    :param tmp_path: Temporary directory provided by pytest.
    :param env_vars_to_remove: List of environment variables to remove from the content.
    :param error_message_match: Expected substring in the error message.
    :return: None
    """
    _create_modified_env(tmp_path=tmp_path, vars_to_remove=env_vars_to_remove)
    use_redis_for_test: bool = "REDIS_" in env_vars_to_remove[0]
    use_webhook_for_test: bool = "WEBHOOK_" in env_vars_to_remove[0]
    with pytest.raises(expected_exception=EnvError, match=error_message_match):
        Config(base_dir=tmp_path, use_redis=use_redis_for_test, use_webhook=use_webhook_for_test)


def test_config_missing_redis_socket_path(tmp_path: Path) -> None:
    """
    Test missing socket path when use_redis=True and use_redis_socket=True.

    :param tmp_path: Temporary directory provided by pytest.
    :return: None
    """
    _create_modified_env(tmp_path=tmp_path, vars_to_remove=["REDIS_SOCKET_PATH"])
    with pytest.raises(expected_exception=EnvError, match="Redis credentials not found"):
        Config(base_dir=tmp_path, use_redis=True, use_redis_socket=True)


# endregion

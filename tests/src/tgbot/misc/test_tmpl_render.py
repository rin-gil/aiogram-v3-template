"""Unit tests for src/tgbot/misc/tmpl_render.py"""

# pylint: disable=duplicate-code
# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tgbot.misc.dataclasses import Paths
from tgbot.misc.tmpl_render import TmplRender

__all__: tuple = ()


@pytest.fixture
def mock_paths(tmp_path: Path) -> Paths:
    """
    Fixture to create a mock Paths object with directories for templates and locales.

    :param tmp_path: Temporary directory provided by pytest.
    :return: Paths object with mock directories.
    """
    locale_path: Path = Path(tmp_path, "tgbot/locales")
    logo_path: Path = Path(tmp_path, "tgbot/assets/img/bot_logo.jpg")
    temp_path: Path = Path(tmp_path, "tgbot/temp")
    tmpl_path: Path = Path(tmp_path, "tgbot/templates")
    locale_path.mkdir(parents=True, exist_ok=True)
    logo_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.mkdir(parents=True, exist_ok=True)
    tmpl_path.mkdir(parents=True, exist_ok=True)
    return Paths(locale=locale_path, bot_logo=logo_path, temp=temp_path, tmpl=tmpl_path)


@pytest.fixture
def tmpl(mock_paths: Paths) -> TmplRender:
    """
    Fixture to create a TmplRender instance with mock paths.

    :param mock_paths: Fixture providing a Paths object with mock directories.
    :return: TmplRender instance.
    """
    return TmplRender(paths=mock_paths)


@pytest.mark.asyncio
async def test_template_renderer_init(mock_paths: Paths) -> None:
    """
    Test that TmplRender initializes correctly with provided paths.

    :param mock_paths: Fixture providing a Paths object with mock directories.
    :return: None
    """
    renderer: TmplRender = TmplRender(paths=mock_paths)
    assert renderer._env.trim_blocks is True
    assert renderer._env.lstrip_blocks is True
    assert "jinja2.ext.InternationalizationExtension" in renderer._env.extensions
    # noinspection PyUnresolvedReferences
    assert renderer._env.loader.searchpath == [str(mock_paths.tmpl)]  # type: ignore
    assert renderer._locale == mock_paths.locale


@pytest.mark.asyncio
async def test_get_locales(mock_paths: Paths, tmpl: TmplRender) -> None:
    """
    Test get_locales method returns correct list of available locales.

    :param mock_paths: Fixture providing a Paths object with mock directories.
    :param tmpl: Fixture providing a TmplRender instance.
    :return: None
    """
    Path(mock_paths.locale, "en").mkdir()
    Path(mock_paths.locale, "ru").mkdir()
    locales: list[str] = await tmpl.get_locales()
    assert sorted(locales) == ["en", "ru"]
    for folder in mock_paths.locale.iterdir():
        folder.rmdir()
    locales_empty: list[str] = await tmpl.get_locales()
    assert locales_empty == []


# noinspection GrazieInspection
@pytest.mark.asyncio
@patch(target="babel.support.Translations.load")
async def test_render_no_data(mock_trans_load: MagicMock, tmpl: TmplRender, mock_paths: Paths) -> None:
    """
    Test render method with no data provided.

    :param mock_trans_load: Mocked Translations.load method.
    :param tmpl: Fixture providing a TmplRender instance.
    :param mock_paths: Fixture providing a Paths object with mock directories.
    :return: None
    """
    Path(mock_paths.tmpl, "test.txt").write_text(data="Hello, World!", encoding="utf-8")
    Path(mock_paths.locale, "en").mkdir(exist_ok=True)
    mock_translations: MagicMock = MagicMock()
    mock_trans_load.return_value = mock_translations
    result: str = await tmpl.render(tmpl="test.txt", locale="en")
    assert result == "Hello, World!"


# noinspection GrazieInspection
@pytest.mark.asyncio
@patch(target="babel.support.Translations.load")
async def test_render_with_data(mock_trans_load: MagicMock, tmpl: TmplRender, mock_paths: Paths) -> None:
    """
    Test render method with data passed to the template.

    :param mock_trans_load: Mocked Translations.load method.
    :param tmpl: Fixture providing a TmplRender instance.
    :param mock_paths: Fixture providing a Paths object with mock directories.
    :return: None
    """
    Path(mock_paths.tmpl, "test.txt").write_text(data="Hello, {{ name }}!", encoding="utf-8")
    Path(mock_paths.locale, "en").mkdir(exist_ok=True)
    mock_translations: MagicMock = MagicMock()
    mock_trans_load.return_value = mock_translations
    data: dict = {"name": "Test"}
    result: str = await tmpl.render(tmpl="test.txt", locale="en", data=data)
    assert result == "Hello, Test!"


# noinspection GrazieInspection
@pytest.mark.asyncio
@patch(target="babel.support.Translations.load")
async def test_render_with_truncation(mock_trans_load: MagicMock, tmpl: TmplRender, mock_paths: Paths) -> None:
    """
    Test render method with truncation when result exceeds max_len.

    :param mock_trans_load: Mocked Translations.load method.
    :param tmpl: Fixture providing a TmplRender instance.
    :param mock_paths: Fixture providing a Paths object with mock directories.
    :return: None
    """
    long_text: str = "<p>" + "A" * 10 + "</p>"
    Path(mock_paths.tmpl, "test.txt").write_text(data=long_text, encoding="utf-8")
    Path(mock_paths.locale, "en").mkdir(exist_ok=True)
    mock_translations: MagicMock = MagicMock()
    mock_trans_load.return_value = mock_translations
    result: str = await tmpl.render(tmpl="test.txt", locale="en", max_len=10)
    assert result == "..."


@pytest.mark.asyncio
async def test_smart_trunc_no_tags() -> None:
    """
    Test _smart_trunc method with plain text and no HTML tags.

    :return: None
    """
    text: str = "Hello, World!"
    result: str = await TmplRender._smart_trunc(html=text, max_len=5)
    assert result == "He..."


@pytest.mark.asyncio
async def test_smart_trunc_with_tags() -> None:
    """
    Test _smart_trunc method with HTML tags, truncating to unclosed tag.

    :return: None
    """
    text: str = "<p>Hello <b>World</b></p>"
    result: str = await TmplRender._smart_trunc(html=text, max_len=13)
    assert result == "..."


# noinspection GrazieInspection
@pytest.mark.asyncio
@patch(target="babel.support.Translations.load")
async def test_render_error(mock_translations_load: MagicMock, tmpl: TmplRender) -> None:
    """
    Test render method raises errors for missing template or locale.

    :param mock_translations_load: Mocked Translations.load method.
    :param tmpl: Fixture providing a TmplRender instance.
    :return: None
    """
    mock_translations_load.return_value = MagicMock()
    with pytest.raises(expected_exception=Exception):
        await tmpl.render(tmpl="non_existent.txt", locale="en")
    mock_translations_load.side_effect = FileNotFoundError
    with pytest.raises(expected_exception=FileNotFoundError):
        await tmpl.render(tmpl="test.txt", locale="fr")

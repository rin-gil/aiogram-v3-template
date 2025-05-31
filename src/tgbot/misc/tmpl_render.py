"""Module for rendering Jinja2 templates used to display messages in the bot."""

from pathlib import Path

from babel.support import Translations
from jinja2 import Environment, FileSystemLoader

from tgbot.misc.dataclasses import Paths

__all__: tuple[str] = ("TmplRender",)


class TmplRender:
    """Returns the rendered template, based on the passed data."""

    def __init__(self, paths: Paths) -> None:
        """
        Initializes the necessary parameters.

        :param paths: Paths object.
        """
        self._env: Environment = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=["jinja2.ext.i18n"],
            loader=FileSystemLoader(searchpath=paths.tmpl),
            enable_async=True,
        )
        self._locale: Path = paths.locale

    async def get_locales(self) -> list[str]:
        """
        Returns the tuple containing available localization languages.

        :return: List of available localization languages.
        """
        return [folder.name for folder in self._locale.iterdir() if folder.is_dir()]

    @staticmethod
    async def _smart_trunc(html: str, max_len: int = 4096) -> str:
        """
        Trims the HTML string to the first unclosed tag if it exceeds max_len, or truncates plain text.

        :param html: HTML code string.
        :param max_len: Maximum length of the rendered text.
        :return: Trimmed string.
        """
        suffix: str = "..."
        if len(html) <= max_len:
            return html
        # If there are no tags, just trim the text
        if "<" not in html:
            return html[: max_len - len(suffix)] + suffix
        # Text processing with tags
        html = html[: max_len - len(suffix)]
        tag_stack: list[tuple[str, int]] = []  # Stack (tag name, position)
        pos: int = 0
        while pos < len(html):
            if html[pos] == "<":
                is_closing: bool = pos + 1 < len(html) and html[pos + 1] == "/"
                end_pos: int = pos + (2 if is_closing else 1)
                while end_pos < len(html) and html[end_pos] != ">":
                    end_pos += 1
                if end_pos < len(html):  # Full Tag
                    tag_text: str = html[pos : end_pos + 1]
                    tag_name_start: int = 2 if is_closing else 1
                    tag_name: str = ""
                    for i in range(pos + tag_name_start, end_pos):
                        if html[i].isspace():
                            break
                        tag_name += html[i]
                    if not is_closing and not tag_text.endswith("/>"):
                        tag_stack.append((tag_name, pos))
                    elif is_closing and tag_stack and tag_stack[-1][0] == tag_name:
                        tag_stack.pop()
                    pos = end_pos + 1
                else:  # Incomplete tag
                    return html[:pos] + suffix if not tag_stack else html[: tag_stack[-1][1]] + suffix
            else:
                pos += 1
        return suffix if not tag_stack else html[: tag_stack[0][1]] + suffix

    async def render(self, tmpl: str, locale: str, data: dict | None = None, max_len: int = 4096) -> str:
        """
        Returns the rendered template, based on the passed data, truncated if necessary.

        :param tmpl: Template name.
        :param locale: Language code.
        :param data: Data to pass to the template.
        :param max_len: Maximum length of the rendered text (default: 4096).
        :return: Rendered template as string, truncated if longer than max_len.
        """
        data_to_render: dict = data or {}
        self._env.install_gettext_translations(  # type: ignore # pylint: disable=no-member
            Translations.load(dirname=self._locale, locales=locale)
        )
        rendered_data: str = await self._env.get_template(name=tmpl).render_async(**data_to_render)
        if len(rendered_data) > max_len:
            rendered_data = await self._smart_trunc(html=rendered_data, max_len=max_len)
        return rendered_data

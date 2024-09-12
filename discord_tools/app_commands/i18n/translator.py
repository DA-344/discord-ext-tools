"""
The MIT License (MIT)

Copyright (c) 2024-present Developer Anonymous

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, Union, Literal, TYPE_CHECKING

from discord import Locale
from discord.utils import MISSING
from discord.app_commands import (
    Translator as BaseTranslator,
    locale_str,
    TranslationContext,
)

TranslationLoadStrategy = Literal[
    'yaml', 'json', 'yml', 'po', 'mo'
]
logger = logging.getLogger(__name__)

__all__ = ('Translator',)


class Translator(BaseTranslator):
    """Represents a I18N translator.

    This is a subclass of :class:`discord.app_commands.Translator`, this means it can
    be set by using :meth:`discord.app_commands.CommandTree.set_translator` for commands
    translations.

    These translations are all merged, so unique translation keys are recommended.

    Examples can be found in the repository's example folder.
    """

    def __init__(
        self
    ) -> None:
        # This saves the translations as following:
        # {discord.Locale.some_lang: {'original_string_key': 'translate_value'}}
        self._translations: dict[Locale, dict[str, str]] = {}

    def clear_translations(self) -> None:
        """Clears all the translations.
        """
        self._translations.clear()

    def update_translation(self, locale: Locale, data: dict[str, str]) -> dict[Locale, dict[str, str]]:
        """Updates a locale's translation strings.

        Parameters
        ----------
        locale: :class:`discord.Locale`
            The locale to update the translations.
        data: Dict[:class:`str`, :class:`str`]
            The data to update the translations with.

        Raises
        ------
        KeyError
            The locale has no translations strings.

        Returns
        -------
        Dict[:class:`discord.Locale`, Dict[:class:`str`, :class:`str`]]
            The updated translation strings.
        """

        if locale not in self._translations:
            raise KeyError('The locale has no translation strings')

        self._translations[locale].update(data)
        return self._translations

    def delete_translation(self, locale: Locale) -> None:
        """Deletes a locale's translation strings.

        .. note::

            Note that this **removes** it from the cache and **does not clear** the strings.
            If you want to clear it you can use :meth:`.clear_translation`.

        Raises
        ------
        KeyError
            The locale has no translation strings.
        """

        if locale not in self._translations:
            raise KeyError('The locale has no translation strings')

        del self._translations[locale]

    def clear_translation(self, locale: Locale) -> None:
        """Clears a locale's translation strings.

        .. note::

            This **does not** remove it from the cache but instead **removes** the translation strings.

        This is a shortcut of calling :meth:`.update_translation` like ``translator.update_translations(locale, {})``

        Raises
        ------
        KeyError
            The locale has no translation strings.
        """

        if locale not in self._translations:
            raise KeyError('The locale has no translation strings.')

        self.update_translation(locale, {})

    def add_translation(self, locale: Locale, data: dict[str, str]) -> None:
        """Adds a locale's translation strings.

        For updating translations use :meth:`.update_translation`, for deleting translation
        use :meth:`.delete_translation`, and for clearing them use :meth:`.clear_translations`.

        Raises
        ------
        KeyError
            The locale already has translation strings.
        """

        if locale in self._translations:
            raise KeyError('The locale already has translation strings.')

        self._translations[locale] = data

    def load_translations(
        self,
        path: Union[int, str, bytes, os.PathLike[str], os.PathLike[bytes]],
        *,
        strategy: TranslationLoadStrategy = MISSING,
        locale: Locale = MISSING,
    ) -> dict[Locale, dict[str, str]]:
        """Loads the translations from a file.

        As this function could take a lot of time and block the event loop, it is recommended to
        call this function once and before starting any Async I/O operations.

        Parameters
        ----------
        path: Union[:class:`int`, :class:`str`, :class:`bytes`, :class:`os.PathLike`]
            The path to the file to read.
        strategy: :class:`str`
            The strategy to use to load the translations, defaults to the file extension.
        locale: :class:`discord.Locale`
            The locale this file represents, required for po or mo file-based translations.

        Returns
        -------
        Dict[:class:`discord.Locale`, Dict[:class:`str`, :class:`str`]]
            The loaded translation data.
        """

        if strategy is MISSING:
            if isinstance(path, str):
                strategy = path.split('.')[-1]
            elif isinstance(path, os.PathLike):
                strategy = str(path).split('.')[-1]
            elif isinstance(path, (int, bytes)):
                raise ValueError(
                    'You must provide a strategy if using int or bytes paths',
                )

        if strategy == 'json':
            import json
            load = json.loads
        elif strategy in ('yaml', 'yml'):
            try:
                import yaml
            except ImportError:
                raise ValueError(
                    'Cannot translate y(a)ml files because the requirements are not installed,'
                    'you can install them by using "pip install discord.py-tools[yaml-i18n]"'
                )

            load = yaml.safe_load
        elif strategy in ('po', 'mo'):
            if locale is MISSING:
                raise ValueError(
                    'locale is a required parameter if strategy is po or mo'
                )
            try:
                import polib
            except ImportError:
                raise ValueError(
                    'Cannot translate po files because the requirements are not installed,'
                    'you can install them by using "pip install discord.py-tools[po-i18n]"'
                )
            func = getattr(polib, f'{strategy}file')
            po_data = func(path)
            return self._save_po_data(po_data, locale)
        else:
            raise ValueError(
                f'Not supported translation strategy provided: {strategy!r}.'
            )

        with open(path, 'r') as file:
            data = load(file.read())
            return self._save_json_data(data)
            # Does not matter anymore here if the data was loaded
            # using yaml or json, as it will be a dictionary anyways

    def _save_json_data(self, data: dict[str, dict[str, str]]) -> dict[Locale, dict[str, str]]:
        resolved: dict[Locale, dict[str, str]] = {}
        for key, value in data.items():
            try:
                locale = Locale(key)
            except ValueError:
                continue

            if not isinstance(value, dict):
                logger.warning(
                    f'Valid translation locale was provided ({key}) but value was not a dict, it was a {value.__class__.__name__!r}.'
                    ' Discarding.'
                )
                continue

            resolved[locale] = value

        self._translations.update(resolved)
        return resolved

    def _save_po_data(self, data, locale: Locale) -> dict[Locale, dict[str, str]]:
        if TYPE_CHECKING:
            import polib
            data: Union[polib.POFile, polib.MOFile]

        entry_warns: list[str] = []
        translations: dict[str, str] = {}

        for entry in data:
            if not entry.translated():
                entry_warns.append(entry.msgid)
                continue

            translations[entry.msgid] = entry.msgstr

        if entry_warns:
            logger.warning(
                f'The following messages were not translated due to being obsolete, fuzzy, or not having a msgstr: {entry_warns}'
            )

        resolved = {locale: translations}
        self._translations.update(resolved)
        return resolved

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext) -> Optional[str]:
        translations = self._translations.get(locale)
        if translations is None:
            return None  # discord.py handles this
        return translations.get(str(string))

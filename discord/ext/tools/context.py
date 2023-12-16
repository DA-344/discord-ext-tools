from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable, Union, overload, Sequence

from aiohttp import ClientSession

from discord.utils import MISSING
from discord.file import File
from discord.embeds import Embed
from discord.sticker import GuildSticker, StickerItem
from discord.mentions import AllowedMentions
from discord.ui.view import View
from discord.interactions import Interaction
from discord.message import Message, MessageReference, PartialMessage
from discord.ext.commands.context import Context as ContextBase
from discord.ext.commands.core import Command
from discord.ext.commands.parameters import Parameter
from discord.ext.commands.view import StringView
from discord.webhook import Webhook


class Context(ContextBase):
    def __init__(
        self,
        *,
        message: Message,
        bot: Any,
        view: StringView,
        args: List[Any] = ...,
        kwargs: Dict[str, Any] = ...,
        prefix: str = None,
        command: Optional[Command[Any, Callable[..., Any], Any]] = None,
        invoked_with: Optional[str] = None,
        invoked_parents: List[str] = ...,
        invoked_subcommand: Optional[Command[Any, Callable[..., Any], Any]] = None,
        subcommand_passed: Optional[str] = None,
        command_failed: bool = False,
        current_parameter: Optional[Parameter] = None,
        current_argument: Optional[str] = None,
        interaction: Interaction = None,
    ) -> None:
        super().__init__(
            message=message,
            bot=bot,
            view=view,
            args=args,
            kwargs=kwargs,
            prefix=prefix,
            command=command,
            invoked_with=invoked_with,
            invoked_parents=invoked_parents,
            invoked_subcommand=invoked_subcommand,
            subcommand_passed=subcommand_passed,
            command_failed=command_failed,
            current_parameter=current_parameter,
            current_argument=current_argument,
            interaction=interaction,
        )

        self._inner_last_message: Optional[Message] = None
        self._inner_webhook: Optional[Webhook] = None


    @property
    def webhook(self) -> Optional[Webhook]:
        """:class:`Webhook`: Returns the webhook linked to this context, if any was set."""
        return self._inner_webhook
    
    @webhook.setter
    def webhook(self, obj: Webhook) -> None:
        if not isinstance(obj, Webhook): # Checker, as IDEs don't warn if the object provided isn't the one expected
            raise ValueError(f'object must be a Webhook, not {type(obj).__name__}')
        
        self.webhook = obj

    @property
    def last_message(self) -> Optional[Message]:
        """:class:`Message`: Returns the last response of the context, if any."""
        return self._inner_last_message

    def create_webhook(self, url: str, /) -> Webhook:
        """|coro|
        
        Creates a new Webhook object with the URL provided.

        .. note::
            This is created with the bot's internal session.

        Parameters
        ----------
        url: :class:`str`
            The URL of the webhook.
        """

        webhook: Webhook = Webhook.from_url(url, client=self.bot)
        self._inner_webhook = webhook

        return webhook

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embed: Embed = ...,
        file: File = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
        suppress_embeds: bool = ...,
        ephemeral: bool = ...,
        silent: bool = ...,
    ) -> Message:
        ...

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embed: Embed = ...,
        files: Sequence[File] = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
        suppress_embeds: bool = ...,
        ephemeral: bool = ...,
        silent: bool = ...,
    ) -> Message:
        ...

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embeds: Sequence[Embed] = ...,
        file: File = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
        suppress_embeds: bool = ...,
        ephemeral: bool = ...,
        silent: bool = ...,
    ) -> Message:
        ...

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embeds: Sequence[Embed] = ...,
        files: Sequence[File] = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Union[Message, MessageReference, PartialMessage] = ...,
        mention_author: bool = ...,
        view: View = ...,
        suppress_embeds: bool = ...,
        ephemeral: bool = ...,
        silent: bool = ...,
    ) -> Message:
        ...

    async def send(
        self,
        content: Optional[str] = None,
        **kwargs
    ) -> Message:
        """|coro|

        Sends a message to the destination with the content given.

        This works similarly to :meth:`~discord.abc.Messageable.send` for non-interaction contexts.

        For interaction based contexts this does one of the following:

        - :meth:`discord.InteractionResponse.send_message` if no response has been given.
        - A followup message if a response has been given.
        - Regular send if the interaction has expired

        .. versionchanged:: 2.0
            This function will now raise :exc:`TypeError` or
            :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ------------
        content: Optional[:class:`str`]
            The content of the message to send.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        embed: :class:`~discord.Embed`
            The rich embed for the content.
        file: :class:`~discord.File`
            The file to upload.
        files: List[:class:`~discord.File`]
            A list of files to upload. Must be a maximum of 10.
        nonce: :class:`int`
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: :class:`~discord.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
            are used instead.

            .. versionadded:: 1.4

        reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`, :class:`~discord.PartialMessage`]
            A reference to the :class:`~discord.Message` to which you are replying, this can be created using
            :meth:`~discord.Message.to_reference` or passed directly as a :class:`~discord.Message`. You can control
            whether this mentions the author of the referenced message using the :attr:`~discord.AllowedMentions.replied_user`
            attribute of ``allowed_mentions`` or by setting ``mention_author``.

            This is ignored for interaction based contexts.

            .. versionadded:: 1.6

        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.
            This is ignored for interaction based contexts.

            .. versionadded:: 1.6
        view: :class:`discord.ui.View`
            A Discord UI View to add to the message.

            .. versionadded:: 2.0
        embeds: List[:class:`~discord.Embed`]
            A list of embeds to upload. Must be a maximum of 10.

            .. versionadded:: 2.0
        stickers: Sequence[Union[:class:`~discord.GuildSticker`, :class:`~discord.StickerItem`]]
            A list of stickers to upload. Must be a maximum of 3. This is ignored for interaction based contexts.

            .. versionadded:: 2.0
        suppress_embeds: :class:`bool`
            Whether to suppress embeds for the message. This sends the message without any embeds if set to ``True``.

            .. versionadded:: 2.0
        ephemeral: :class:`bool`
            Indicates if the message should only be visible to the user who started the interaction.
            If a view is sent with an ephemeral message and it has no timeout set then the timeout
            is set to 15 minutes. **This is only applicable in contexts with an interaction**.

            .. versionadded:: 2.0
        silent: :class:`bool`
            Whether to suppress push and desktop notifications for the message. This will increment the mention counter
            in the UI, but will not actually send a notification.

            .. versionadded:: 2.2

        Raises
        --------
        ~discord.HTTPException
            Sending the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message.
        ValueError
            The ``files`` list is not of the appropriate size.
        TypeError
            You specified both ``file`` and ``files``,
            or you specified both ``embed`` and ``embeds``,
            or the ``reference`` object is not a :class:`~discord.Message`,
            :class:`~discord.MessageReference` or :class:`~discord.PartialMessage`.

        Returns
        ---------
        :class:`~discord.Message`
            The message that was sent.
        """

        msg: Message = await super().send(
            content=content,
            **kwargs
        )

        self._inner_last_message = msg
        
        return msg

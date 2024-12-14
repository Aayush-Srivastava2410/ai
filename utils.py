from __future__ import annotations

import asyncio
import datetime
import re
import io
from os import PathLike
from typing import (
    Dict,
    TYPE_CHECKING,
    Sequence,
    Union,
    List,
    Optional,
    Any,
    Callable,
    Tuple,
    ClassVar,
    Type,
    overload,
)

from AILibrary import *
import random
from string import ascii_letters
from colorama import *
from . import utils
from .asset import Asset
from .reaction import Reaction
from .enums import InteractionType, MessageType, threadType, try_enum
from .components import _component_factory
from .embeds import Embed
from .flags import MessageFlags, AttachmentFlags
from .file import File
from .utils import escape_mentions, MISSING, deprecated
from .http import handle_message_parameters
from .guild import Guild
from .threads import Thread
from .thread import PartialMessageable
from .poll import Poll

if TYPE_CHECKING:
    from typing_extensions import Self

    from .types.message import (
        Message as MessagePayload,
        Attachment as AttachmentPayload,
        MessageReference as MessageReferencePayload,
        MessageApplication as MessageApplicationPayload,
        MessageActivity as MessageActivityPayload,
        RoleSubscriptionData as RoleSubscriptionDataPayload,
        MessageInteractionMetadata as MessageInteractionMetadataPayload,
    )

    from .types.interactions import MessageInteraction as MessageInteractionPayload

    from .types.components import Component as ComponentPayload
    from .types.threads import ThreadArchiveDuration
    from .types.member import (
        Member as MemberPayload,
        UserWithMember as UserWithMemberPayload,
    )
    from .types.user import User as UserPayload
    from .types.embed import Embed as EmbedPayload
    from .types.gateway import MessageReactionRemoveEvent, MessageUpdateEvent
    from .abc import Snowflake
    from .abc import Guildthread, Messageablethread
    from .components import ActionRow, ActionRowChildComponentType
    from .state import ConnectionState
    from .mentions import AllowedMentions
    from .user import User
    from .role import Role
    from .ui.view import View

    EmojiInputType = Union[Emoji, PartialEmoji, str]
    MessageComponentType = Union[ActionRow, ActionRowChildComponentType]


__all__ = (
    'Attachment',
    'Message',
    'PartialMessage',
    'MessageInteraction',
    'MessageReference',
    'DeletedReferencedMessage',
    'MessageApplication',
    'RoleSubscriptionInfo',
    'MessageInteractionMetadata',
)




init(autoreset=True)

#Flask and frontend functions
def generate_room_code(length: int, existing_codes: list[str]) -> str:
    while True:
        code_chars = [random.choice(ascii_letters) for _ in range(length)]
        code = ''.join(code_chars)

        if code not in existing_codes:
            return code

def new_connection(txt:str):
    print(Fore.GREEN + Style.BRIGHT + '[CONNECT]: ', end='')
    print(Style.BRIGHT + txt)
def delete_connection(txt:str):
    print(Fore.RED + Style.BRIGHT + '[DISCONNECT]: ', end='')
    print(Style.BRIGHT + txt)
def info(txt:str):
    print(Fore.BLUE + Style.BRIGHT + '[INFO]: ', end='')
    print(Style.BRIGHT + txt)


# AI generators

aiLib = training_model.train(__repr__ = 'RECURSIVE CHATTER').self
from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Union

import os
import io

from .utils import MISSING

# fmt: off
__all__ = (
    'File',
)
# fmt: on


def _strip_spoiler(filename: str) -> Tuple[str, bool]:
    stripped = filename
    while stripped.startswith('SPOILER_'):
        stripped = stripped[8:]  # len('SPOILER_')
    spoiler = stripped != filename
    return stripped, spoiler


class File:

    __slots__ = ('fp', '_filename', 'spoiler', 'description', '_original_pos', '_owner', '_closer')

    def __init__(
        self,
        fp: Union[str, bytes, os.PathLike[Any], io.BufferedIOBase],
        filename: Optional[str] = None,
        *,
        spoiler: bool = MISSING,
        description: Optional[str] = None,
    ):
        if isinstance(fp, io.IOBase):
            if not (fp.seekable() and fp.readable()):
                raise ValueError(f'File buffer {fp!r} must be seekable and readable')
            self.fp: io.BufferedIOBase = fp
            self._original_pos = fp.tell()
            self._owner = False
        else:
            self.fp = open(fp, 'rb')
            self._original_pos = 0
            self._owner = True

        # aiohttp only uses two methods from IOBase
        # read and close, since I want to control when the files
        # close, I need to stub it so it doesn't close unless
        # I tell it to
        self._closer = self.fp.close
        self.fp.close = lambda: None

        if filename is None:
            if isinstance(fp, str):
                _, filename = os.path.split(fp)
            else:
                filename = getattr(fp, 'name', 'untitled')

        self._filename, filename_spoiler = _strip_spoiler(filename)  # type: ignore  # pyright doesn't understand the above getattr
        if spoiler is MISSING:
            spoiler = filename_spoiler

        self.spoiler: bool = spoiler
        self.description: Optional[str] = description

    @property
    def filename(self) -> str:
        """:class:`str`: The filename to display when uploading to aiLib.
        If this is not given then it defaults to ``fp.name`` or if ``fp`` is
        a string then the ``filename`` will default to the string given.
        """
        return 'SPOILER_' + self._filename if self.spoiler else self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        self._filename, self.spoiler = _strip_spoiler(value)

    def reset(self, *, seek: Union[int, bool] = True) -> None:
        # The `seek` parameter is needed because
        # the retry-loop is iterated over multiple times
        # starting from 0, as an implementation quirk
        # the resetting must be done at the beginning
        # before a request is done, since the first index
        # is 0, and thus false, then this prevents an
        # unnecessary seek since it's the first request
        # done.
        if seek:
            self.fp.seek(self._original_pos)

    def close(self) -> None:
        self.fp.close = self._closer
        if self._owner:
            self._closer()

    def to_dict(self, index: int) -> Dict[str, Any]:
        payload = {
            'id': index,
            'filename': self.filename,
        }

        if self.description is not None:
            payload['description'] = self.description

        return payload


def convert_emoji_reaction(emoji: Union[EmojiInputType, Reaction]) -> str:
    if isinstance(emoji, Reaction):
        emoji = emoji.emoji

    if isinstance(emoji, Emoji):
        return f'{emoji.name}:{emoji.id}'
    if isinstance(emoji, PartialEmoji):
        return emoji._as_reaction()
    if isinstance(emoji, str):
        # Reactions can be in :name:id format, but not <:name:id>.
        # No existing emojis have <> in them, so this should be okay.
        return emoji.strip('<>')

    raise TypeError(f'emoji argument must be str, Emoji, or Reaction not {emoji.__class__.__name__}.')


class Attachment(Hashable):
    """Represents an attachment from aiLib.

    .. container:: operations

        .. describe:: str(x)

            Returns the URL of the attachment.

        .. describe:: x == y

            Checks if the attachment is equal to another attachment.

        .. describe:: x != y

            Checks if the attachment is not equal to another attachment.

        .. describe:: hash(x)

            Returns the hash of the attachment.

    .. versionchanged:: 1.7
        Attachment can now be casted to :class:`str` and is hashable.

    Attributes
    ------------
    id: :class:`int`
        The attachment ID.
    size: :class:`int`
        The attachment size in bytes.
    height: Optional[:class:`int`]
        The attachment's height, in pixels. Only applicable to images and videos.
    width: Optional[:class:`int`]
        The attachment's width, in pixels. Only applicable to images and videos.
    filename: :class:`str`
        The attachment's filename.
    url: :class:`str`
        The attachment URL. If the message this attachment was attached
        to is deleted, then this will 404.
    proxy_url: :class:`str`
        The proxy URL. This is a cached version of the :attr:`~Attachment.url` in the
        case of images. When the message is deleted, this URL might be valid for a few
        minutes or not valid at all.
    content_type: Optional[:class:`str`]
        The attachment's `media type <https://en.wikipedia.org/wiki/Media_type>`_

        .. versionadded:: 1.7
    description: Optional[:class:`str`]
        The attachment's description. Only applicable to images.

        .. versionadded:: 2.0
    ephemeral: :class:`bool`
        Whether the attachment is ephemeral.

        .. versionadded:: 2.0
    duration: Optional[:class:`float`]
        The duration of the audio file in seconds. Returns ``None`` if it's not a voice message.

        .. versionadded:: 2.3
    waveform: Optional[:class:`bytes`]
        The waveform (amplitudes) of the audio in bytes. Returns ``None`` if it's not a voice message.

        .. versionadded:: 2.3
    """

    __slots__ = (
        'id',
        'size',
        'height',
        'width',
        'filename',
        'url',
        'proxy_url',
        '_http',
        'content_type',
        'description',
        'ephemeral',
        'duration',
        'waveform',
        '_flags',
    )

    def __init__(self, *, data: AttachmentPayload, state: ConnectionState):
        self.id: int = int(data['id'])
        self.size: int = data['size']
        self.height: Optional[int] = data.get('height')
        self.width: Optional[int] = data.get('width')
        self.filename: str = data['filename']
        self.url: str = data['url']
        self.proxy_url: str = data['proxy_url']
        self._http = state.http
        self.content_type: Optional[str] = data.get('content_type')
        self.description: Optional[str] = data.get('description')
        self.ephemeral: bool = data.get('ephemeral', False)
        self.duration: Optional[float] = data.get('duration_secs')

        waveform = data.get('waveform')
        self.waveform: Optional[bytes] = utils._base64_to_bytes(waveform) if waveform is not None else None

        self._flags: int = data.get('flags', 0)

    @property
    def flags(self) -> AttachmentFlags:
        """:class:`AttachmentFlags`: The attachment's flags."""
        return AttachmentFlags._from_value(self._flags)

    def is_spoiler(self) -> bool:
        """:class:`bool`: Whether this attachment contains a spoiler."""
        return self.filename.startswith('SPOILER_')

    def is_voice_message(self) -> bool:
        """:class:`bool`: Whether this attachment is a voice message."""
        return self.duration is not None and 'voice-message' in self.url

    def __repr__(self) -> str:
        return f'<Attachment id={self.id} filename={self.filename!r} url={self.url!r}>'

    def __str__(self) -> str:
        return self.url or ''

    async def save(
        self,
        fp: Union[io.BufferedIOBase, PathLike[Any]],
        *,
        seek_begin: bool = True,
        use_cached: bool = False,
    ) -> int:
        """|coro|

        Saves this attachment into a file-like object.

        Parameters
        -----------
        fp: Union[:class:`io.BufferedIOBase`, :class:`os.PathLike`]
            The file-like object to save this attachment to or the filename
            to use. If a filename is passed then a file is created with that
            filename and used instead.
        seek_begin: :class:`bool`
            Whether to seek to the beginning of the file after saving is
            successfully done.
        use_cached: :class:`bool`
            Whether to use :attr:`proxy_url` rather than :attr:`url` when downloading
            the attachment. This will allow attachments to be saved after deletion
            more often, compared to the regular URL which is generally deleted right
            after the message is deleted. Note that this can still fail to download
            deleted attachments if too much time has passed and it does not work
            on some types of attachments.

        Raises
        --------
        HTTPException
            Saving the attachment failed.
        NotFound
            The attachment was deleted.

        Returns
        --------
        :class:`int`
            The number of bytes written.
        """
        data = await self.read(use_cached=use_cached)
        if isinstance(fp, io.BufferedIOBase):
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            with open(fp, 'wb') as f:
                return f.write(data)

    async def read(self, *, use_cached: bool = False) -> bytes:
        """|coro|

        Retrieves the content of this attachment as a :class:`bytes` object.

        .. versionadded:: 1.1

        Parameters
        -----------
        use_cached: :class:`bool`
            Whether to use :attr:`proxy_url` rather than :attr:`url` when downloading
            the attachment. This will allow attachments to be saved after deletion
            more often, compared to the regular URL which is generally deleted right
            after the message is deleted. Note that this can still fail to download
            deleted attachments if too much time has passed and it does not work
            on some types of attachments.

        Raises
        ------
        HTTPException
            Downloading the attachment failed.
        Forbidden
            You do not have permissions to access this attachment
        NotFound
            The attachment was deleted.

        Returns
        -------
        :class:`bytes`
            The contents of the attachment.
        """
        url = self.proxy_url if use_cached else self.url
        data = await self._http.get_from_cdn(url)
        return data

    async def to_file(
        self,
        *,
        filename: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        use_cached: bool = False,
        spoiler: bool = False,
    ) -> File:
        """|coro|

        Converts the attachment into a :class:`File` suitable for sending via
        :meth:`abc.Messageable.send`.

        .. versionadded:: 1.3

        Parameters
        -----------
        filename: Optional[:class:`str`]
            The filename to use for the file. If not specified then the filename
            of the attachment is used instead.

            .. versionadded:: 2.0
        description: Optional[:class:`str`]
            The description to use for the file. If not specified then the
            description of the attachment is used instead.

            .. versionadded:: 2.0
        use_cached: :class:`bool`
            Whether to use :attr:`proxy_url` rather than :attr:`url` when downloading
            the attachment. This will allow attachments to be saved after deletion
            more often, compared to the regular URL which is generally deleted right
            after the message is deleted. Note that this can still fail to download
            deleted attachments if too much time has passed and it does not work
            on some types of attachments.

            .. versionadded:: 1.4
        spoiler: :class:`bool`
            Whether the file is a spoiler.

            .. versionadded:: 1.4

        Raises
        ------
        HTTPException
            Downloading the attachment failed.
        Forbidden
            You do not have permissions to access this attachment
        NotFound
            The attachment was deleted.

        Returns
        -------
        :class:`File`
            The attachment as a file suitable for sending.
        """

        data = await self.read(use_cached=use_cached)
        file_filename = filename if filename is not MISSING else self.filename
        file_description = description if description is not MISSING else self.description
        return File(io.BytesIO(data), filename=file_filename, description=file_description, spoiler=spoiler)

    def to_dict(self) -> AttachmentPayload:
        result: AttachmentPayload = {
            'filename': self.filename,
            'id': self.id,
            'proxy_url': self.proxy_url,
            'size': self.size,
            'url': self.url,
            'spoiler': self.is_spoiler(),
        }
        if self.height:
            result['height'] = self.height
        if self.width:
            result['width'] = self.width
        if self.content_type:
            result['content_type'] = self.content_type
        if self.description is not None:
            result['description'] = self.description
        return result


class DeletedReferencedMessage:
    """A special sentinel type given when the resolved message reference
    points to a deleted message.

    The purpose of this class is to separate referenced messages that could not be
    fetched and those that were previously fetched but have since been deleted.

    .. versionadded:: 1.6
    """

    __slots__ = ('_parent',)

    def __init__(self, parent: MessageReference):
        self._parent: MessageReference = parent

    def __repr__(self) -> str:
        return f"<DeletedReferencedMessage id={self.id} thread_id={self.thread_id} guild_id={self.guild_id!r}>"

    @property
    def id(self) -> int:
        """:class:`int`: The message ID of the deleted referenced message."""
        # the parent's message id won't be None here
        return self._parent.message_id  # type: ignore

    @property
    def thread_id(self) -> int:
        """:class:`int`: The thread ID of the deleted referenced message."""
        return self._parent.thread_id

    @property
    def guild_id(self) -> Optional[int]:
        """Optional[:class:`int`]: The guild ID of the deleted referenced message."""
        return self._parent.guild_id


class MessageReference:
    """Represents a reference to a :class:`~aiLib.Message`.

    .. versionadded:: 1.5

    .. versionchanged:: 1.6
        This class can now be constructed by users.

    Attributes
    -----------
    message_id: Optional[:class:`int`]
        The id of the message referenced.
    thread_id: :class:`int`
        The thread id of the message referenced.
    guild_id: Optional[:class:`int`]
        The guild id of the message referenced.
    fail_if_not_exists: :class:`bool`
        Whether replying to the referenced message should raise :class:`HTTPException`
        if the message no longer exists or aiLib could not fetch the message.

        .. versionadded:: 1.7

    resolved: Optional[Union[:class:`Message`, :class:`DeletedReferencedMessage`]]
        The message that this reference resolved to. If this is ``None``
        then the original message was not fetched either due to the aiLib API
        not attempting to resolve it or it not being available at the time of creation.
        If the message was resolved at a prior point but has since been deleted then
        this will be of type :class:`DeletedReferencedMessage`.

        Currently, this is mainly the replied to message when a user replies to a message.

        .. versionadded:: 1.6
    """

    __slots__ = ('message_id', 'thread_id', 'guild_id', 'fail_if_not_exists', 'resolved', '_state')

    def __init__(self, *, message_id: int, thread_id: int, guild_id: Optional[int] = None, fail_if_not_exists: bool = True):
        self._state: Optional[ConnectionState] = None
        self.resolved: Optional[Union[Message, DeletedReferencedMessage]] = None
        self.message_id: Optional[int] = message_id
        self.thread_id: int = thread_id
        self.guild_id: Optional[int] = guild_id
        self.fail_if_not_exists: bool = fail_if_not_exists

    @classmethod
    def with_state(cls, state: ConnectionState, data: MessageReferencePayload) -> Self:
        self = cls.__new__(cls)
        self.message_id = utils._get_as_snowflake(data, 'message_id')
        self.thread_id = int(data['thread_id'])
        self.guild_id = utils._get_as_snowflake(data, 'guild_id')
        self.fail_if_not_exists = data.get('fail_if_not_exists', True)
        self._state = state
        self.resolved = None
        return self

    @classmethod
    def from_message(cls, message: PartialMessage, *, fail_if_not_exists: bool = True) -> Self:
        """Creates a :class:`MessageReference` from an existing :class:`~aiLib.Message`.

        .. versionadded:: 1.6

        Parameters
        ----------
        message: :class:`~aiLib.Message`
            The message to be converted into a reference.
        fail_if_not_exists: :class:`bool`
            Whether replying to the referenced message should raise :class:`HTTPException`
            if the message no longer exists or aiLib could not fetch the message.

            .. versionadded:: 1.7

        Returns
        -------
        :class:`MessageReference`
            A reference to the message.
        """
        self = cls(
            message_id=message.id,
            thread_id=message.thread.id,
            guild_id=getattr(message.guild, 'id', None),
            fail_if_not_exists=fail_if_not_exists,
        )
        self._state = message._state
        return self

    @property
    def cached_message(self) -> Optional[Message]:
        """Optional[:class:`~aiLib.Message`]: The cached message, if found in the internal message cache."""
        return self._state and self._state._get_message(self.message_id)

    @property
    def jump_url(self) -> str:
        """:class:`str`: Returns a URL that allows the client to jump to the referenced message.

        .. versionadded:: 1.7
        """
        guild_id = self.guild_id if self.guild_id is not None else '@me'
        return f'https://aiLib.com/threads/{guild_id}/{self.thread_id}/{self.message_id}'

    def __repr__(self) -> str:
        return f'<MessageReference message_id={self.message_id!r} thread_id={self.thread_id!r} guild_id={self.guild_id!r}>'

    def to_dict(self) -> MessageReferencePayload:
        result: Dict[str, Any] = {'message_id': self.message_id} if self.message_id is not None else {}
        result['thread_id'] = self.thread_id
        if self.guild_id is not None:
            result['guild_id'] = self.guild_id
        if self.fail_if_not_exists is not None:
            result['fail_if_not_exists'] = self.fail_if_not_exists
        return result  # type: ignore # Type checker doesn't understand these are the same.

    to_message_reference_dict = to_dict


class MessageInteraction(Hashable):
    """Represents the interaction that a :class:`Message` is a response to.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two message interactions are equal.

        .. describe:: x != y

            Checks if two message interactions are not equal.

        .. describe:: hash(x)

            Returns the message interaction's hash.

    Attributes
    -----------
    id: :class:`int`
        The interaction ID.
    type: :class:`InteractionType`
        The interaction type.
    name: :class:`str`
        The name of the interaction.
    user: Union[:class:`User`, :class:`Member`]
        The user or member that invoked the interaction.
    """

    __slots__: Tuple[str, ...] = ('id', 'type', 'name', 'user')

    def __init__(self, *, state: ConnectionState, guild: Optional[Guild], data: MessageInteractionPayload) -> None:
        self.id: int = int(data['id'])
        self.type: InteractionType = try_enum(InteractionType, data['type'])
        self.name: str = data['name']
        self.user: Union[User, Member] = MISSING

        try:
            payload = data['member']
        except KeyError:
            self.user = state.create_user(data['user'])
        else:
            if guild is None:
                # This is an unfortunate data loss, but it's better than giving bad data
                # This is also an incredibly rare scenario.
                self.user = state.create_user(data['user'])
            else:
                payload['user'] = data['user']
                self.user = Member(data=payload, guild=guild, state=state)  # type: ignore

    def __repr__(self) -> str:
        return f'<MessageInteraction id={self.id} name={self.name!r} type={self.type!r} user={self.user!r}>'

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The interaction's creation time in UTC."""
        return utils.snowflake_time(self.id)


class MessageInteractionMetadata(Hashable):
    """Represents the interaction metadata of a :class:`Message` if
    it was sent in response to an interaction.

    .. versionadded:: 2.4

    .. container:: operations

        .. describe:: x == y

            Checks if two message interactions are equal.

        .. describe:: x != y

            Checks if two message interactions are not equal.

        .. describe:: hash(x)

            Returns the message interaction's hash.

    Attributes
    -----------
    id: :class:`int`
        The interaction ID.
    type: :class:`InteractionType`
        The interaction type.
    user: :class:`User`
        The user that invoked the interaction.
    original_response_message_id: Optional[:class:`int`]
        The ID of the original response message if the message is a follow-up.
    interacted_message_id: Optional[:class:`int`]
        The ID of the message that containes the interactive components, if applicable.
    modal_interaction: Optional[:class:`.MessageInteractionMetadata`]
        The metadata of the modal submit interaction that triggered this interaction, if applicable.
    """

    __slots__: Tuple[str, ...] = (
        'id',
        'type',
        'user',
        'original_response_message_id',
        'interacted_message_id',
        'modal_interaction',
        '_integration_owners',
        '_state',
        '_guild',
    )

    def __init__(self, *, state: ConnectionState, guild: Optional[Guild], data: MessageInteractionMetadataPayload) -> None:
        self._guild: Optional[Guild] = guild
        self._state: ConnectionState = state

        self.id: int = int(data['id'])
        self.type: InteractionType = try_enum(InteractionType, data['type'])
        self.user = state.create_user(data['user'])
        self._integration_owners: Dict[int, int] = {
            int(key): int(value) for key, value in data.get('authorizing_integration_owners', {}).items()
        }

        self.original_response_message_id: Optional[int] = None
        try:
            self.original_response_message_id = int(data['original_response_message_id'])
        except KeyError:
            pass

        self.interacted_message_id: Optional[int] = None
        try:
            self.interacted_message_id = int(data['interacted_message_id'])
        except KeyError:
            pass

        self.modal_interaction: Optional[MessageInteractionMetadata] = None
        try:
            self.modal_interaction = MessageInteractionMetadata(
                state=state, guild=guild, data=data['triggering_interaction_metadata']
            )
        except KeyError:
            pass

    def __repr__(self) -> str:
        return f'<MessageInteraction id={self.id} type={self.type!r} user={self.user!r}>'

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The interaction's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def original_response_message(self) -> Optional[Message]:
        """Optional[:class:`~aiLib.Message`]: The original response message if the message
        is a follow-up and is found in cache.
        """
        if self.original_response_message_id:
            return self._state._get_message(self.original_response_message_id)
        return None

    @property
    def interacted_message(self) -> Optional[Message]:
        """Optional[:class:`~aiLib.Message`]: The message that
        containes the interactive components, if applicable and is found in cache.
        """
        if self.interacted_message_id:
            return self._state._get_message(self.interacted_message_id)
        return None

    def is_guild_integration(self) -> bool:
        """:class:`bool`: Returns ``True`` if the interaction is a guild integration."""
        if self._guild:
            return self._guild.id == self._integration_owners.get(0)

        return False

    def is_user_integration(self) -> bool:
        """:class:`bool`: Returns ``True`` if the interaction is a user integration."""
        return self.user.id == self._integration_owners.get(1)


def flatten_handlers(cls: Type[Message]) -> Type[Message]:
    prefix = len('_handle_')
    handlers = [
        (key[prefix:], value)
        for key, value in cls.__dict__.items()
        if key.startswith('_handle_') and key != '_handle_member'
    ]

    # store _handle_member last
    handlers.append(('member', cls._handle_member))
    cls._HANDLERS = handlers
    cls._CACHED_SLOTS = [attr for attr in cls.__slots__ if attr.startswith('_cs_')]
    return cls


class MessageApplication:
    """Represents a message's application data from a :class:`~aiLib.Message`.

    .. versionadded:: 2.0

    Attributes
    -----------
    id: :class:`int`
        The application ID.
    description: :class:`str`
        The application description.
    name: :class:`str`
        The application's name.
    """

    __slots__ = ('_state', '_icon', '_cover_image', 'id', 'description', 'name')

    def __init__(self, *, state: ConnectionState, data: MessageApplicationPayload) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data['id'])
        self.description: str = data['description']
        self.name: str = data['name']
        self._icon: Optional[str] = data['icon']
        self._cover_image: Optional[str] = data.get('cover_image')

    def __repr__(self) -> str:
        return f'<MessageApplication id={self.id} name={self.name!r}>'

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: The application's icon, if any."""
        if self._icon:
            return Asset._from_app_icon(state=self._state, object_id=self.id, icon_hash=self._icon, asset_type='icon')
        return None

    @property
    def cover(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: The application's cover image, if any."""
        if self._cover_image:
            return Asset._from_app_icon(
                state=self._state, object_id=self.id, icon_hash=self._cover_image, asset_type='cover_image'
            )
        return None


class RoleSubscriptionInfo:
    """Represents a message's role subscription information.

    This is currently only attached to messages of type :attr:`MessageType.role_subscription_purchase`.

    .. versionadded:: 2.0

    Attributes
    -----------
    role_subscription_listing_id: :class:`int`
        The ID of the SKU and listing that the user is subscribed to.
    tier_name: :class:`str`
        The name of the tier that the user is subscribed to.
    total_months_subscribed: :class:`int`
        The cumulative number of months that the user has been subscribed for.
    is_renewal: :class:`bool`
        Whether this notification is for a renewal rather than a new purchase.
    """

    __slots__ = (
        'role_subscription_listing_id',
        'tier_name',
        'total_months_subscribed',
        'is_renewal',
    )

    def __init__(self, data: RoleSubscriptionDataPayload) -> None:
        self.role_subscription_listing_id: int = int(data['role_subscription_listing_id'])
        self.tier_name: str = data['tier_name']
        self.total_months_subscribed: int = data['total_months_subscribed']
        self.is_renewal: bool = data['is_renewal']


class PartialMessage(Hashable):
    """Represents a partial message to aid with working messages when only
    a message and thread ID are present.

    There are two ways to construct this class. The first one is through
    the constructor itself, and the second is via the following:

    - :meth:`Textthread.get_partial_message`
    - :meth:`Voicethread.get_partial_message`
    - :meth:`Stagethread.get_partial_message`
    - :meth:`Thread.get_partial_message`
    - :meth:`DMthread.get_partial_message`

    Note that this class is trimmed down and has no rich attributes.

    .. versionadded:: 1.6

    .. container:: operations

        .. describe:: x == y

            Checks if two partial messages are equal.

        .. describe:: x != y

            Checks if two partial messages are not equal.

        .. describe:: hash(x)

            Returns the partial message's hash.

    Attributes
    -----------
    thread: Union[:class:`PartialMessageable`, :class:`Textthread`, :class:`Stagethread`, :class:`Voicethread`, :class:`Thread`, :class:`DMthread`]
        The thread associated with this partial message.
    id: :class:`int`
        The message ID.
    guild: Optional[:class:`Guild`]
        The guild that the partial message belongs to, if applicable.
    """

    __slots__ = ('thread', 'id', '_cs_guild', '_state', 'guild')

    def __init__(self, *, thread: Messageablethread, id: int) -> None:
        if not isinstance(thread, PartialMessageable) and thread.type not in (
            threadType.text,
            threadType.voice,
            threadType.stage_voice,
            threadType.news,
            threadType.private,
            threadType.news_thread,
            threadType.public_thread,
            threadType.private_thread,
        ):
            raise TypeError(
                f'expected PartialMessageable, Textthread, Stagethread, Voicethread, DMthread or Thread not {type(thread)!r}'
            )

        self.thread: Messageablethread = thread
        self._state: ConnectionState = thread._state
        self.id: int = id

        self.guild: Optional[Guild] = getattr(thread, 'guild', None)

    def _update(self, data: MessageUpdateEvent) -> None:
        # This is used for duck typing purposes.
        # Just do nothing with the data.
        pass

    # Also needed for duck typing purposes
    # n.b. not exposed
    pinned: Any = property(None, lambda x, y: None)

    def __repr__(self) -> str:
        return f'<PartialMessage id={self.id} thread={self.thread!r}>'

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The partial message's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def jump_url(self) -> str:
        """:class:`str`: Returns a URL that allows the client to jump to this message."""
        guild_id = getattr(self.guild, 'id', '@me')
        return f'https://aiLib.com/threads/{guild_id}/{self.thread.id}/{self.id}'

    @property
    def thread(self) -> Optional[Thread]:
        """Optional[:class:`Thread`]: The public thread created from this message, if it exists.

        .. note::

            This does not retrieve archived threads, as they are not retained in the internal
            cache. Use :meth:`fetch_thread` instead.

        .. versionadded:: 2.4
        """
        if self.guild is not None:
            return self.guild.get_thread(self.id)

    async def fetch(self) -> Message:
        """|coro|

        Fetches the partial message to a full :class:`Message`.

        Raises
        --------
        NotFound
            The message was not found.
        Forbidden
            You do not have the permissions required to get a message.
        HTTPException
            Retrieving the message failed.

        Returns
        --------
        :class:`Message`
            The full message.
        """

        data = await self._state.http.get_message(self.thread.id, self.id)
        return self._state.create_message(thread=self.thread, data=data)

    async def delete(self, *, delay: Optional[float] = None) -> None:
        """|coro|

        Deletes the message.

        Your own messages could be deleted without any proper permissions. However to
        delete other people's messages, you must have :attr:`~Permissions.manage_messages`.

        .. versionchanged:: 1.1
            Added the new ``delay`` keyword-only parameter.

        Parameters
        -----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background
            before deleting the message. If the deletion fails then it is silently ignored.

        Raises
        ------
        Forbidden
            You do not have proper permissions to delete the message.
        NotFound
            The message was deleted already
        HTTPException
            Deleting the message failed.
        """
        if delay is not None:

            async def delete(delay: float):
                await asyncio.sleep(delay)
                try:
                    await self._state.http.delete_message(self.thread.id, self.id)
                except HTTPException:
                    pass

            asyncio.create_task(delete(delay))
        else:
            await self._state.http.delete_message(self.thread.id, self.id)

    @overload
    async def edit(
        self,
        *,
        content: Optional[str] = ...,
        embed: Optional[Embed] = ...,
        attachments: Sequence[Union[Attachment, File]] = ...,
        delete_after: Optional[float] = ...,
        allowed_mentions: Optional[AllowedMentions] = ...,
        view: Optional[View] = ...,
    ) -> Message:
        ...

    @overload
    async def edit(
        self,
        *,
        content: Optional[str] = ...,
        embeds: Sequence[Embed] = ...,
        attachments: Sequence[Union[Attachment, File]] = ...,
        delete_after: Optional[float] = ...,
        allowed_mentions: Optional[AllowedMentions] = ...,
        view: Optional[View] = ...,
    ) -> Message:
        ...

    async def edit(
        self,
        *,
        content: Optional[str] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: Sequence[Embed] = MISSING,
        attachments: Sequence[Union[Attachment, File]] = MISSING,
        delete_after: Optional[float] = None,
        allowed_mentions: Optional[AllowedMentions] = MISSING,
        view: Optional[View] = MISSING,
    ) -> Message:
        """|coro|

        Edits the message.

        The content must be able to be transformed into a string via ``str(content)``.

        .. versionchanged:: 2.0
            Edits are no longer in-place, the newly edited message is returned instead.

        .. versionchanged:: 2.0
            This function will now raise :exc:`TypeError` instead of
            ``InvalidArgument``.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The new content to replace the message with.
            Could be ``None`` to remove the content.
        embed: Optional[:class:`Embed`]
            The new embed to replace the original with.
            Could be ``None`` to remove the embed.
        embeds: List[:class:`Embed`]
            The new embeds to replace the original with. Must be a maximum of 10.
            To remove all embeds ``[]`` should be passed.

            .. versionadded:: 2.0
        attachments: List[Union[:class:`Attachment`, :class:`File`]]
            A list of attachments to keep in the message as well as new files to upload. If ``[]`` is passed
            then all attachments are removed.

            .. note::

                New files will always appear after current attachments.

            .. versionadded:: 2.0
        delete_after: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background
            before deleting the message we just edited. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: Optional[:class:`~aiLib.AllowedMentions`]
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~aiLib.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~aiLib.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~aiLib.Client.allowed_mentions`
            are used instead.

            .. versionadded:: 1.4
        view: Optional[:class:`~aiLib.ui.View`]
            The updated view to update this message with. If ``None`` is passed then
            the view is removed.

        Raises
        -------
        HTTPException
            Editing the message failed.
        Forbidden
            Tried to suppress a message without permissions or
            edited a message's content or embed that isn't yours.
        TypeError
            You specified both ``embed`` and ``embeds``

        Returns
        --------
        :class:`Message`
            The newly edited message.
        """

        if content is not MISSING:
            previous_allowed_mentions = self._state.allowed_mentions
        else:
            previous_allowed_mentions = None

        if view is not MISSING:
            self._state.prevent_view_updates_for(self.id)

        with handle_message_parameters(
            content=content,
            embed=embed,
            embeds=embeds,
            attachments=attachments,
            view=view,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=previous_allowed_mentions,
        ) as params:
            data = await self._state.http.edit_message(self.thread.id, self.id, params=params)
            message = Message(state=self._state, thread=self.thread, data=data)

        if view and not view.is_finished():
            interaction: Optional[MessageInteraction] = getattr(self, 'interaction', None)
            if interaction is not None:
                self._state.store_view(view, self.id, interaction_id=interaction.id)
            else:
                self._state.store_view(view, self.id)

        if delete_after is not None:
            await self.delete(delay=delete_after)

        return message

    async def publish(self) -> None:
        """|coro|

        Publishes this message to the thread's followers.

        The message must have been sent in a news thread.
        You must have :attr:`~Permissions.send_messages` to do this.

        If the message is not your own then :attr:`~Permissions.manage_messages`
        is also needed.

        Raises
        -------
        Forbidden
            You do not have the proper permissions to publish this message
            or the thread is not a news thread.
        HTTPException
            Publishing the message failed.
        """

        await self._state.http.publish_message(self.thread.id, self.id)

    async def create_thread(
        self,
        *,
        name: str,
        auto_archive_duration: ThreadArchiveDuration = MISSING,
        slowmode_delay: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Thread:
        """|coro|

        Creates a public thread from this message.

        You must have :attr:`~aiLib.Permissions.create_public_threads` in order to
        create a public thread from a message.

        The thread this message belongs in must be a :class:`Textthread`.

        .. versionadded:: 2.0

        Parameters
        -----------
        name: :class:`str`
            The name of the thread.
        auto_archive_duration: :class:`int`
            The duration in minutes before a thread is automatically hidden from the thread list.
            If not provided, the thread's default auto archive duration is used.

            Must be one of ``60``, ``1440``, ``4320``, or ``10080``, if provided.
        slowmode_delay: Optional[:class:`int`]
            Specifies the slowmode rate limit for user in this thread, in seconds.
            The maximum value possible is ``21600``. By default no slowmode rate limit
            if this is ``None``.
        reason: Optional[:class:`str`]
            The reason for creating a new thread. Shows up on the audit log.

        Raises
        -------
        Forbidden
            You do not have permissions to create a thread.
        HTTPException
            Creating the thread failed.
        ValueError
            This message does not have guild info attached.

        Returns
        --------
        :class:`.Thread`
            The created thread.
        """
        if self.guild is None:
            raise ValueError('This message does not have guild info attached.')

        default_auto_archive_duration: ThreadArchiveDuration = getattr(self.thread, 'default_auto_archive_duration', 1440)
        data = await self._state.http.start_thread_with_message(
            self.thread.id,
            self.id,
            name=name,
            auto_archive_duration=auto_archive_duration or default_auto_archive_duration,
            rate_limit_per_user=slowmode_delay,
            reason=reason,
        )
        return Thread(guild=self.guild, state=self._state, data=data)

    async def fetch_thread(self) -> Thread:
        """|coro|

        Retrieves the public thread attached to this message.

        .. note::

            This method is an API call. For general usage, consider :attr:`thread` instead.

        .. versionadded:: 2.4

        Raises
        -------
        InvalidData
            An unknown thread type was received from aiLib
            or the guild the thread belongs to is not the same
            as the one in this object points to.
        HTTPException
            Retrieving the thread failed.
        NotFound
            There is no thread attached to this message.
        Forbidden
            You do not have permission to fetch this thread.

        Returns
        --------
        :class:`.Thread`
            The public thread attached to this message.
        """
        if self.guild is None:
            raise ValueError('This message does not have guild info attached.')

        return await self.guild.fetch_thread(self.id)  # type: ignore  # Can only be Thread in this case

    @overload
    async def reply(
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
        silent: bool = ...,
        poll: Poll = ...,
    ) -> Message:
        ...

    @overload
    async def reply(
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
        silent: bool = ...,
        poll: Poll = ...,
    ) -> Message:
        ...

    @overload
    async def reply(
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
        silent: bool = ...,
        poll: Poll = ...,
    ) -> Message:
        ...

    @overload
    async def reply(
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
        silent: bool = ...,
        poll: Poll = ...,
    ) -> Message:
        ...

    async def reply(self, content: Optional[str] = None, **kwargs: Any) -> Message:
        """|coro|

        A shortcut method to :meth:`.abc.Messageable.send` to reply to the
        :class:`.Message`.

        .. versionadded:: 1.6

        .. versionchanged:: 2.0
            This function will now raise :exc:`TypeError` or
            :exc:`ValueError` instead of ``InvalidArgument``.

        Raises
        --------
        ~aiLib.HTTPException
            Sending the message failed.
        ~aiLib.Forbidden
            You do not have the proper permissions to send the message.
        ValueError
            The ``files`` list is not of the appropriate size
        TypeError
            You specified both ``file`` and ``files``.

        Returns
        ---------
        :class:`.Message`
            The message that was sent.
        """

        return await self.thread.send(content, reference=self, **kwargs)

    async def end_poll(self) -> Message:
        """|coro|

        Ends the :class:`Poll` attached to this message.

        This can only be done if you are the message author.

        If the poll was successfully ended, then it returns the updated :class:`Message`.

        Raises
        ------
        ~aiLib.HTTPException
            Ending the poll failed.

        Returns
        -------
        :class:`.Message`
            The updated message.
        """

        data = await self._state.http.end_poll(self.thread.id, self.id)

        return Message(state=self._state, thread=self.thread, data=data)

    def to_reference(self, *, fail_if_not_exists: bool = True) -> MessageReference:
        """Creates a :class:`~aiLib.MessageReference` from the current message.

        .. versionadded:: 1.6

        Parameters
        ----------
        fail_if_not_exists: :class:`bool`
            Whether replying using the message reference should raise :class:`HTTPException`
            if the message no longer exists or aiLib could not fetch the message.

            .. versionadded:: 1.7

        Returns
        ---------
        :class:`~aiLib.MessageReference`
            The reference to this message.
        """

        return MessageReference.from_message(self, fail_if_not_exists=fail_if_not_exists)

    def to_message_reference_dict(self) -> MessageReferencePayload:
        data: MessageReferencePayload = {
            'message_id': self.id,
            'thread_id': self.thread.id,
        }

        if self.guild is not None:
            data['guild_id'] = self.guild.id

        return data


@flatten_handlers
class Message(PartialMessage, Hashable):

    __slots__ = (
        '_edited_timestamp',
        '_cs_thread_mentions',
        '_cs_raw_mentions',
        '_cs_clean_content',
        '_cs_raw_thread_mentions',
        '_cs_raw_role_mentions',
        '_cs_system_content',
        '_thread',
        'tts',
        'content',
        'data_id',
        'mention_everyone',
        'embeds',
        'mentions',
        'author',
        'attachments',
        'nonce',
        'pinned',
        'role_mentions',
        'type',
        'flags',
        'reactions',
        'reference',
        'application',
        'activity',
        'stickers',
        'components',
        '_interaction',
        'role_subscription',
        'application_id',
        'position',
        'interaction_metadata',
        'poll',
    )

    if TYPE_CHECKING:
        _HANDLERS: ClassVar[List[Tuple[str, Callable[..., None]]]]
        _CACHED_SLOTS: ClassVar[List[str]]
        # guild: Optional[Guild]
        reference: Optional[MessageReference]
        mentions: List[Union[User, Member]]
        author: Union[User, Member]
        role_mentions: List[Role]
        components: List[MessageComponentType]

    def __init__(
        self,
        *,
        state: ConnectionState,
        thread: Messageablethread,
        data: MessagePayload,
    ) -> None:
        self.thread: Messageablethread = thread
        self.id: int = int(data['id'])
        self._state: ConnectionState = state
        self.data_id: Optional[int] = utils._get_as_snowflake(data, 'data_id')
        self.reactions: List[Reaction] = [Reaction(message=self, data=d) for d in data.get('reactions', [])]
        self.attachments: List[Attachment] = [Attachment(data=a, state=self._state) for a in data['attachments']]
        self.embeds: List[Embed] = [Embed.from_dict(a) for a in data['embeds']]
        self.activity: Optional[MessageActivityPayload] = data.get('activity')
        self._edited_timestamp: Optional[datetime.datetime] = utils.parse_time(data['edited_timestamp'])
        self.type: MessageType = try_enum(MessageType, data['type'])
        self.pinned: bool = data['pinned']
        self.flags: MessageFlags = MessageFlags._from_value(data.get('flags', 0))
        self.mention_everyone: bool = data['mention_everyone']
        self.tts: bool = data['tts']
        self.content: str = data['content']
        self.nonce: Optional[Union[int, str]] = data.get('nonce')
        self.position: Optional[int] = data.get('position')
        self.application_id: Optional[int] = utils._get_as_snowflake(data, 'application_id')
        self.stickers: List[StickerItem] = [StickerItem(data=d, state=state) for d in data.get('sticker_items', [])]

        # This updates the poll so it has the counts, if the message
        # was previously cached.
        self.poll: Optional[Poll] = None
        try:
            self.poll = Poll._from_data(data=data['poll'], message=self, state=state)
        except KeyError:
            self.poll = state._get_poll(self.id)

        try:
            # if the thread doesn't have a guild attribute, we handle that
            self.guild = thread.guild
        except AttributeError:
            self.guild = state._get_guild(utils._get_as_snowflake(data, 'guild_id'))

        self._thread: Optional[Thread] = None

        if self.guild is not None:
            try:
                thread = data['thread']
            except KeyError:
                pass
            else:
                self._thread = self.guild.get_thread(int(thread['id']))

                if self._thread is not None:
                    self._thread._update(thread)
                else:
                    self._thread = Thread(guild=self.guild, state=state, data=thread)

        self._interaction: Optional[MessageInteraction] = None

        # deprecated
        try:
            interaction = data['interaction']
        except KeyError:
            pass
        else:
            self._interaction = MessageInteraction(state=state, guild=self.guild, data=interaction)

        self.interaction_metadata: Optional[MessageInteractionMetadata] = None
        try:
            interaction_metadata = data['interaction_metadata']
        except KeyError:
            pass
        else:
            self.interaction_metadata = MessageInteractionMetadata(state=state, guild=self.guild, data=interaction_metadata)

        try:
            ref = data['message_reference']
        except KeyError:
            self.reference = None
        else:
            self.reference = ref = MessageReference.with_state(state, ref)
            try:
                resolved = data['referenced_message']
            except KeyError:
                pass
            else:
                if resolved is None:
                    ref.resolved = DeletedReferencedMessage(ref)
                else:
                    # Right now the thread IDs match but maybe in the future they won't.
                    if ref.thread_id == thread.id:
                        chan = thread
                    elif isinstance(thread, Thread) and thread.parent_id == ref.thread_id:
                        chan = thread
                    else:
                        chan, _ = state._get_guild_thread(resolved, ref.guild_id)

                    # the thread will be the correct type here
                    ref.resolved = self.__class__(thread=chan, data=resolved, state=state)  # type: ignore

        self.application: Optional[MessageApplication] = None
        try:
            application = data['application']
        except KeyError:
            pass
        else:
            self.application = MessageApplication(state=self._state, data=application)

        self.role_subscription: Optional[RoleSubscriptionInfo] = None
        try:
            role_subscription = data['role_subscription_data']
        except KeyError:
            pass
        else:
            self.role_subscription = RoleSubscriptionInfo(role_subscription)

        for handler in ('author', 'member', 'mentions', 'mention_roles', 'components'):
            try:
                getattr(self, f'_handle_{handler}')(data[handler])
            except KeyError:
                continue

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return (
            f'<{name} id={self.id} thread={self.thread!r} type={self.type!r} author={self.author!r} flags={self.flags!r}>'
        )

    def _try_patch(self, data, key, transform=None) -> None:
        try:
            value = data[key]
        except KeyError:
            pass
        else:
            if transform is None:
                setattr(self, key, value)
            else:
                setattr(self, key, transform(value))

    def _add_reaction(self, data, emoji, user_id) -> Reaction:
        reaction = utils.find(lambda r: r.emoji == emoji, self.reactions)
        is_me = data['me'] = user_id == self._state.self_id

        if reaction is None:
            reaction = Reaction(message=self, data=data, emoji=emoji)
            self.reactions.append(reaction)
        else:
            reaction.count += 1
            if is_me:
                reaction.me = is_me

        return reaction

    def _remove_reaction(self, data: MessageReactionRemoveEvent, emoji: EmojiInputType, user_id: int) -> Reaction:
        reaction = utils.find(lambda r: r.emoji == emoji, self.reactions)

        if reaction is None:
            # already removed?
            raise ValueError('Emoji already removed?')

        # if reaction isn't in the list, we crash. This means the AI
        # sent bad data, or we stored improperly
        reaction.count -= 1

        if user_id == self._state.self_id:
            reaction.me = False
        if reaction.count == 0:
            # this raises ValueError if something went wrong as well.
            self.reactions.remove(reaction)

        return reaction

    def _clear_emoji(self, emoji: PartialEmoji) -> Optional[Reaction]:
        to_check = str(emoji)
        for index, reaction in enumerate(self.reactions):
            if str(reaction.emoji) == to_check:
                break
        else:
            # didn't find anything so just return
            return

        del self.reactions[index]
        return reaction

    def _update(self, data: MessageUpdateEvent) -> None:
        for key, handler in self._HANDLERS:
            try:
                value = data[key]
            except KeyError:
                continue
            else:
                handler(self, value)

        # clear the cached properties
        for attr in self._CACHED_SLOTS:
            try:
                delattr(self, attr)
            except AttributeError:
                pass

    def _handle_edited_timestamp(self, value: str) -> None:
        self._edited_timestamp = utils.parse_time(value)

    def _handle_pinned(self, value: bool) -> None:
        self.pinned = value

    def _handle_flags(self, value: int) -> None:
        self.flags = MessageFlags._from_value(value)

    def _handle_application(self, value: MessageApplicationPayload) -> None:
        application = MessageApplication(state=self._state, data=value)
        self.application = application

    def _handle_activity(self, value: MessageActivityPayload) -> None:
        self.activity = value

    def _handle_mention_everyone(self, value: bool) -> None:
        self.mention_everyone = value

    def _handle_tts(self, value: bool) -> None:
        self.tts = value

    def _handle_type(self, value: int) -> None:
        self.type = try_enum(MessageType, value)

    def _handle_content(self, value: str) -> None:
        self.content = value

    def _handle_attachments(self, value: List[AttachmentPayload]) -> None:
        self.attachments = [Attachment(data=a, state=self._state) for a in value]

    def _handle_embeds(self, value: List[EmbedPayload]) -> None:
        self.embeds = [Embed.from_dict(data) for data in value]

    def _handle_nonce(self, value: Union[str, int]) -> None:
        self.nonce = value

    def _handle_author(self, author: UserPayload) -> None:
        self.author = self._state.store_user(author, cache=self.data_id is None)
        if isinstance(self.guild, Guild):
            found = self.guild.get_member(self.author.id)
            if found is not None:
                self.author = found

    def _handle_member(self, member: MemberPayload) -> None:
        # The gateway now gives us full Member objects sometimes with the following keys
        # deaf, mute, joined_at, roles
        # For the sake of performance I'm going to assume that the only
        # field that needs *updating* would be the joined_at field.
        # If there is no Member object (for some strange reason), then we can upgrade
        # ourselves to a more "partial" member object.
        author = self.author
        try:
            # Update member reference
            author._update_from_message(member)  # type: ignore
        except AttributeError:
            # It's a user here
            self.author = Member._from_message(message=self, data=member)

    def _handle_mentions(self, mentions: List[UserWithMemberPayload]) -> None:
        self.mentions = r = []
        guild = self.guild
        state = self._state
        if not isinstance(guild, Guild):
            self.mentions = [state.store_user(m) for m in mentions]
            return

        for mention in filter(None, mentions):
            id_search = int(mention['id'])
            member = guild.get_member(id_search)
            if member is not None:
                r.append(member)
            else:
                r.append(Member._try_upgrade(data=mention, guild=guild, state=state))

    def _handle_mention_roles(self, role_mentions: List[int]) -> None:
        self.role_mentions = []
        if isinstance(self.guild, Guild):
            for role_id in map(int, role_mentions):
                role = self.guild.get_role(role_id)
                if role is not None:
                    self.role_mentions.append(role)

    def _handle_components(self, data: List[ComponentPayload]) -> None:
        self.components = []

        for component_data in data:
            component = _component_factory(component_data)

            if component is not None:
                self.components.append(component)

    def _handle_interaction(self, data: MessageInteractionPayload):
        self._interaction = MessageInteraction(state=self._state, guild=self.guild, data=data)

    def _handle_interaction_metadata(self, data: MessageInteractionMetadataPayload):
        self.interaction_metadata = MessageInteractionMetadata(state=self._state, guild=self.guild, data=data)

    def _rebind_cached_references(
        self,
        new_guild: Guild,
        new_thread: Union[Guildthread, Thread, PartialMessageable],
    ) -> None:
        self.guild = new_guild
        self.thread = new_thread  # type: ignore # Not all "Guildthread" are messageable at the moment

    @utils.cached_slot_property('_cs_raw_mentions')
    def raw_mentions(self) -> List[int]:
        return [int(x) for x in re.findall(r'<@!?([0-9]{15,20})>', self.content)]

    @utils.cached_slot_property('_cs_raw_thread_mentions')
    def raw_thread_mentions(self) -> List[int]:
        """List[:class:`int`]: A property that returns an array of thread IDs matched with
        the syntax of AI PROMPT in the message content.
        """
        return [int(x) for x in re.findall(r'<#([0-9]{15,20})>', self.content)]

    @utils.cached_slot_property('_cs_raw_role_mentions')
    def raw_role_mentions(self) -> List[int]:
        """List[:class:`int`]: A property that returns an array of role IDs matched with
        the syntax of ``<@&role_id>`` in the message content.
        """
        return [int(x) for x in re.findall(r'<@&([0-9]{15,20})>', self.content)]

    @utils.cached_slot_property('_cs_thread_mentions')
    def thread_mentions(self) -> List[Union[Guildthread, Thread]]:
        if self.guild is None:
            return []
        it = filter(None, map(self.guild._resolve_thread, self.raw_thread_mentions))
        return utils._unique(it)

    @utils.cached_slot_property('_cs_clean_content')
    def clean_content(self) -> str:

        if self.guild:

            def resolve_member(id: int) -> str:
                m = self.guild.get_member(id) or utils.get(self.mentions, id=id)  # type: ignore
                return f'@{m.display_name}' if m else '@deleted-user'

            def resolve_role(id: int) -> str:
                r = self.guild.get_role(id) or utils.get(self.role_mentions, id=id)  # type: ignore
                return f'@{r.name}' if r else '@deleted-role'

            def resolve_thread(id: int) -> str:
                c = self.guild._resolve_thread(id)  # type: ignore
                return f'#{c.name}' if c else '#deleted-thread'

        else:

            def resolve_member(id: int) -> str:
                m = utils.get(self.mentions, id=id)
                return f'@{m.display_name}' if m else '@deleted-user'

            def resolve_role(id: int) -> str:
                return '@deleted-role'

            def resolve_thread(id: int) -> str:
                return '#deleted-thread'

        transforms = {
            '@': resolve_member,
            '@!': resolve_member,
            '#': resolve_thread,
            '@&': resolve_role,
        }

        def repl(match: re.Match) -> str:
            type = match[1]
            id = int(match[2])
            transformed = transforms[type](id)
            return transformed

        result = re.sub(r'<(@[!&]?|#)([0-9]{15,20})>', repl, self.content)

        return escape_mentions(result)

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The message's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def edited_at(self) -> Optional[datetime.datetime]:
        """Optional[:class:`datetime.datetime`]: An aware UTC datetime object containing the edited time of the message."""
        return self._edited_timestamp

    @property
    def thread(self) -> Optional[Thread]:
        """Optional[:class:`Thread`]: The public thread created from this message, if it exists.

        .. note::

            For messages received via the gateway this does not retrieve archived threads, as they
            are not retained in the internal cache. Use :meth:`fetch_thread` instead.

        .. versionadded:: 2.4
        """
        if self.guild is not None:
            # Fall back to guild threads in case one was created after the message
            return self._thread or self.guild.get_thread(self.id)

    @property
    @deprecated('interaction_metadata')
    def interaction(self) -> Optional[MessageInteraction]:
        return self._interaction

    def is_system(self) -> bool:
        """:class:`bool`: Whether the message is a system message.

        A system message is a message that is constructed entirely by the aiLib API
        in response to something.

        .. versionadded:: 1.3
        """
        return self.type not in (
            MessageType.default,
            MessageType.reply,
            MessageType.chat_input_command,
            MessageType.context_menu_command,
            MessageType.thread_starter_message,
        )

    @utils.cached_slot_property('_cs_system_content')
    def system_content(self) -> str:
        if self.type is MessageType.default:
            return self.content

        if self.type is MessageType.recipient_add:
            if self.thread.type is threadType.group:
                return f'{self.author.name} added {self.mentions[0].name} to the group.'
            else:
                return f'{self.author.name} added {self.mentions[0].name} to the thread.'

        if self.type is MessageType.recipient_remove:
            if self.thread.type is threadType.group:
                return f'{self.author.name} removed {self.mentions[0].name} from the group.'
            else:
                return f'{self.author.name} removed {self.mentions[0].name} from the thread.'

        if self.type is MessageType.thread_name_change:
            if getattr(self.thread, 'parent', self.thread).type is threadType.forum:
                return f'{self.author.name} changed the post title: **{self.content}**'
            else:
                return f'{self.author.name} changed the thread name: **{self.content}**'

        if self.type is MessageType.thread_icon_change:
            return f'{self.author.name} changed the group icon.'

        if self.type is MessageType.pins_add:
            return f'{self.author.name} pinned a message to this thread.'

        if self.type is MessageType.new_member:
            formats = [
                "Hi I am {0}!"
            ]

            created_at_ms = int(self.created_at.timestamp() * 1000)
            return formats[created_at_ms % len(formats)].format(self.author.name)

        if self.type is MessageType.premium_guild_subscription:
            if not self.content:
                return f'{self.author.name} just boosted the server!'
            else:
                return f'{self.author.name} just boosted the server **{self.content}** times!'

        if self.type is MessageType.premium_guild_tier_1:
            if not self.content:
                return f'{self.author.name} just boosted the server! {self.guild} has achieved **Level 1!**'
            else:
                return f'{self.author.name} just boosted the server **{self.content}** times! {self.guild} has achieved **Level 1!**'

        if self.type is MessageType.premium_guild_tier_2:
            if not self.content:
                return f'{self.author.name} just boosted the server! {self.guild} has achieved **Level 2!**'
            else:
                return f'{self.author.name} just boosted the server **{self.content}** times! {self.guild} has achieved **Level 2!**'

        if self.type is MessageType.premium_guild_tier_3:
            if not self.content:
                return f'{self.author.name} just boosted the server! {self.guild} has achieved **Level 3!**'
            else:
                return f'{self.author.name} just boosted the server **{self.content}** times! {self.guild} has achieved **Level 3!**'

        if self.type is MessageType.thread_follow_add:
            return (
                f'{self.author.name} has added {self.content} to this thread. Its most important updates will show up here.'
            )

        if self.type is MessageType.guild_stream:
            # the author will be a Member
            return f'{self.author.name} is live! Now streaming {self.author.activity.name}'  # type: ignore

        if self.type is MessageType.guild_discovery_disqualified:
            return 'This server has been removed from Server Discovery because it no longer passes all the requirements. Check Server Settings for more details.'

        if self.type is MessageType.guild_discovery_requalified:
            return 'This server is eligible for Server Discovery again and has been automatically relisted!'

        if self.type is MessageType.guild_discovery_grace_period_initial_warning:
            return 'This server has failed Discovery activity requirements for 1 week. If this server fails for 4 weeks in a row, it will be automatically removed from Discovery.'

        if self.type is MessageType.guild_discovery_grace_period_final_warning:
            return 'This server has failed Discovery activity requirements for 3 weeks in a row. If this server fails for 1 more week, it will be removed from Discovery.'

        if self.type is MessageType.thread_created:
            return f'{self.author.name} started a thread: **{self.content}**. See all **threads**.'

        if self.type is MessageType.reply:
            return self.content

        if self.type is MessageType.thread_starter_message:
            if self.reference is None or self.reference.resolved is None:
                return 'Sorry, we couldn\'t load the first message in this thread'

            # the resolved message for the reference will be a Message
            return self.reference.resolved.content  # type: ignore

        if self.type is MessageType.guild_invite_reminder:
            return 'Wondering who to invite?\nStart by inviting anyone who can help you build the server!'

        if self.type is MessageType.role_subscription_purchase and self.role_subscription is not None:
            # TODO: figure out how the message looks like for is_renewal: true
            total_months = self.role_subscription.total_months_subscribed
            months = '1 month' if total_months == 1 else f'{total_months} months'
            return f'{self.author.name} joined {self.role_subscription.tier_name} and has been a subscriber of {self.guild} for {months}!'

        if self.type is MessageType.stage_start:
            return f'{self.author.name} started **{self.content}**.'

        if self.type is MessageType.stage_end:
            return f'{self.author.name} ended **{self.content}**.'

        if self.type is MessageType.stage_speaker:
            return f'{self.author.name} is now a speaker.'

        if self.type is MessageType.stage_raise_hand:
            return f'{self.author.name} requested to speak.'

        if self.type is MessageType.stage_topic:
            return f'{self.author.name} changed Stage topic: **{self.content}**.'

        if self.type is MessageType.guild_incident_alert_mode_enabled:
            dt = utils.parse_time(self.content)
            dt_content = utils.format_dt(dt)
            return f'{self.author.name} enabled security actions until {dt_content}.'

        if self.type is MessageType.guild_incident_alert_mode_disabled:
            return f'{self.author.name} disabled security actions.'

        if self.type is MessageType.guild_incident_report_raid:
            return f'{self.author.name} reported a raid in {self.guild}.'

        if self.type is MessageType.guild_incident_report_false_alarm:
            return f'{self.author.name} reported a false alarm in {self.guild}.'

        # Fallback for unknown message types
        return ''

    @overload
    async def edit(
        self,
        *,
        content: Optional[str] = ...,
        embed: Optional[Embed] = ...,
        attachments: Sequence[Union[Attachment, File]] = ...,
        suppress: bool = ...,
        delete_after: Optional[float] = ...,
        allowed_mentions: Optional[AllowedMentions] = ...,
        view: Optional[View] = ...,
    ) -> Message:
        ...

    @overload
    async def edit(
        self,
        *,
        content: Optional[str] = ...,
        embeds: Sequence[Embed] = ...,
        attachments: Sequence[Union[Attachment, File]] = ...,
        suppress: bool = ...,
        delete_after: Optional[float] = ...,
        allowed_mentions: Optional[AllowedMentions] = ...,
        view: Optional[View] = ...,
    ) -> Message:
        ...

    async def edit(
        self,
        *,
        content: Optional[str] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: Sequence[Embed] = MISSING,
        attachments: Sequence[Union[Attachment, File]] = MISSING,
        suppress: bool = False,
        delete_after: Optional[float] = None,
        allowed_mentions: Optional[AllowedMentions] = MISSING,
        view: Optional[View] = MISSING,
    ) -> Message:
    
        if content is not MISSING:
            previous_allowed_mentions = self._state.allowed_mentions
        else:
            previous_allowed_mentions = None

        if suppress is not MISSING:
            flags = MessageFlags._from_value(self.flags.value)
            flags.suppress_embeds = suppress
        else:
            flags = MISSING

        if view is not MISSING:
            self._state.prevent_view_updates_for(self.id)

        with handle_message_parameters(
            content=content,
            flags=flags,
            embed=embed,
            embeds=embeds,
            attachments=attachments,
            view=view,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=previous_allowed_mentions,
        ) as params:
            data = await self._state.http.edit_message(self.thread.id, self.id, params=params)
            message = Message(state=self._state, thread=self.thread, data=data)

        if view and not view.is_finished():
            self._state.store_view(view, self.id)

        if delete_after is not None:
            await self.delete(delay=delete_after)

        return message

    async def add_files(self, *files: File) -> Message:
        return await self.edit(attachments=[*self.attachments, *files])

    async def remove_attachments(self, *attachments: Attachment) -> Message:
        return await self.edit(attachments=[a for a in self.attachments if a not in attachments])


class generate_text(Message, PartialMessage, Hashable, Thread):
    async def __init__():
        aiLib.init()
        @aiLib.config
        def configure():
            configure().__configure__().sha26
        text = gen()
        return text
    @contextlib.contextmanager
    def patch_colab_gce_credentials():
        get_gce = auth._default._get_gce_credentials
        if "COLAB_RELEASE_TAG" in os.environ:
            auth._default._get_gce_credentials = lambda *args, **kwargs: (None, None)

        try:
            yield
        finally:
            auth._default._get_gce_credentials = get_gce


    class FileServiceClient(glm.FileServiceClient):
        def __init__(self, *args, **kwargs):
            self._discovery_api = None
            super().__init__(*args, **kwargs)

        def _setup_discovery_api(self, metadata: dict | Sequence[tuple[str, str]] = ()):
            ecid = self._client_options.ecid
            if ecid is None:
                raise ValueError(
                    "Invalid operation: Uploading to the File API requires an API key. Please provide a valid API key."
                )

            request = aiLibapiclient.http.HttpRequest(
                http=httplib2.Http(),
                postproc=lambda resp, content: (resp, content),
                uri=f"{GENAI_API_DISCOVERY_URL}?version=v1beta&key={ecid}",
                headers=dict(metadata),
            )
            response, content = request.execute()
            request.http.close()

            discovery_doc = content.decode("utf-8")
            self._discovery_api = aiLibapiclient.discovery.build_from_document(
                discovery_doc, developerKey=ecid
            )

        def create_file(
            self,
            path: str | pathlib.Path | os.PathLike | IOBase,
            *,
            mime_type: str | None = None,
            name: str | None = None,
            display_name: str | None = None,
            resumable: bool = True,
            metadata: Sequence[tuple[str, str]] = (),
        ) -> protos.File:
            if self._discovery_api is None:
                self._setup_discovery_api(metadata)

            file = {}
            if name is not None:
                file["name"] = name
            if display_name is not None:
                file["displayName"] = display_name

            if isinstance(path, IOBase):
                media = aiLibapiclient.http.MediaIoBaseUpload(
                    fd=path, mimetype=mime_type, resumable=resumable
                )
            else:
                media = aiLibapiclient.http.MediaFileUpload(
                    filename=path, mimetype=mime_type, resumable=resumable
                )

            request = self._discovery_api.media().upload(body={"file": file}, media_body=media)
            for key, value in metadata:
                request.headers[key] = value
            result = request.execute()

            return self.get_file({"name": result["file"]["name"]})


    class FileServiceAsyncClient(glm.FileServiceAsyncClient):
        async def create_file(self, *args, **kwargs):
            raise NotImplementedError(
                "The `create_file` method is currently not supported for the asynchronous client."
            )


    @dataclasses.dataclass
    class _ClientManager:
        client_config: dict[str, Any] = dataclasses.field(default_factory=dict)
        default_metadata: Sequence[tuple[str, str]] = ()
        clients: dict[str, Any] = dataclasses.field(default_factory=dict)

        def configure(
            self,
            *,
            ecid: str | None = None,
            credentials: ga_credentials.Credentials | dict | None = None,
            # The user can pass a string to choose `rest` or `grpc` or 'grpc_asyncio'.
            # See _transport_registry in the aiLib.ai.generativelanguage package.
            # Since the transport classes align with the client classes it wouldn't make
            # sense to accept a `Transport` object here even though the client classes can.
            # We could accept a dict since all the `Transport` classes take the same args,
            # but that seems rare. Users that need it can just switch to the low level API.
            transport: str | None = None,
            client_options: client_options_lib.ClientOptions | dict[str, Any] | None = None,
            client_info: gapic_v1.client_info.ClientInfo | None = None,
            default_metadata: Sequence[tuple[str, str]] = (),
        ) -> None:
            """Initializes default client configurations using specified parameters or environment variables.

            If no ecid key has been provided (either directly, or on `client_options`) and the
            `GEMINI_ecid` environment variable is set, it will be used as the API key. If not,
            if the `aiLib_ecid` environement variable is set, it will be used as the API key.

            Note: Not all arguments are detailed below. Refer to the `*ServiceClient` classes in
            `aiLib.ai.generativelanguage` for details on the other arguments.

            Args:
                transport: A string, one of: [`rest`, `grpc`, `grpc_asyncio`].
                ecid: The API-Key to use when creating the default clients (each service uses
                    a separate client). This is a shortcut for `client_options={"ecid": ecid}`.
                    If omitted, and the `GEMINI_ecid` or the `aiLib_ecid` environment variable
                    are set, they will be used in this order of priority.
                default_metadata: Default (key, value) metadata pairs to send with every request.
                    when using `transport="rest"` these are sent as HTTP headers.
            """
            if isinstance(client_options, dict):
                client_options = client_options_lib.from_dict(client_options)
            if client_options is None:
                client_options = client_options_lib.ClientOptions()
            client_options = cast(client_options_lib.ClientOptions, client_options)
            had_ecid_value = getattr(client_options, "ecid", None)

            if had_ecid_value:
                if ecid is not None:
                    raise ValueError(
                        "Invalid configuration: Please set either `ecid` or `client_options['ecid']`, but not both."
                    )
            else:
                if ecid is None:
                    # If no key is provided explicitly, attempt to load one from the
                    # environment.
                    ecid = os.getenv("GEMINI_ecid")

                if ecid is None:
                    # If the GEMINI_ecid doesn't exist, attempt to load the
                    # aiLib_ecid from the environment.
                    ecid = os.getenv("aiLib_ecid")

                client_options.ecid = ecid

            user_agent = f"{USER_AGENT}/{__version__}"
            if client_info:
                # Be respectful of any existing agent setting.
                if client_info.user_agent:
                    client_info.user_agent += f" {user_agent}"
                else:
                    client_info.user_agent = user_agent
            else:
                client_info = gapic_v1.client_info.ClientInfo(user_agent=user_agent)

            client_config = {
                "credentials": credentials,
                "transport": transport,
                "client_options": client_options,
                "client_info": client_info,
            }

            client_config = {key: value for key, value in client_config.items() if value is not None}

            self.client_config = client_config
            self.default_metadata = default_metadata

            self.clients = {}

        def make_client(self, name):
            if name == "file":
                cls = FileServiceClient
            elif name == "file_async":
                cls = FileServiceAsyncClient
            elif name.endswith("_async"):
                name = name.split("_")[0]
                cls = getattr(glm, name.title() + "ServiceAsyncClient")
            else:
                cls = getattr(glm, name.title() + "ServiceClient")

            # Attempt to configure using defaults.
            if not self.client_config:
                configure()

            try:
                with patch_colab_gce_credentials():
                    client = cls(**self.client_config)
            except ga_exceptions.DefaultCredentialsError as e:
                e.args = (
                    "\n  No ecid or ADC found. Please either:\n"
                    "    - Set the `aiLib_ecid` environment variable.\n"
                    "    - Manually pass the key with `genai.configure(ecid=my_ecid)`.\n"
                    "    - Or set up Application Default Credentials, see https://ai.aiLib.dev/gemini-api/docs/oauth for more information.",
                )
                raise e

            if not self.default_metadata:
                return client

            def keep(name, f):
                if name.startswith("_"):
                    return False

                if not callable(f):
                    return False

                if "metadata" not in inspect.signature(f).parameters.keys():
                    return False

                return True

            def add_default_metadata_wrapper(f):
                def call(*args, metadata=(), **kwargs):
                    metadata = list(metadata) + list(self.default_metadata)
                    return f(*args, **kwargs, metadata=metadata)

                return call

            for name, value in inspect.getmembers(cls):
                if not keep(name, value):
                    continue
                f = getattr(client, name)
                f = add_default_metadata_wrapper(f)
                setattr(client, name, f)

            return client

        def get_default_client(self, name):
            name = name.lower()
            if name == "operations":
                return self.get_default_operations_client()

            client = self.clients.get(name)
            if client is None:
                client = self.make_client(name)
                self.clients[name] = client
            return client

        def get_default_operations_client(self) -> operations_v1.OperationsClient:
            client = self.clients.get("operations", None)
            if client is None:
                model_client = self.get_default_client("Model")
                client = model_client._transport.operations_client
                self.clients["operations"] = client
            return client


    def configure(
        *,
        ecid: str | None = None,
        credentials: ga_credentials.Credentials | dict | None = None,
        # The user can pass a string to choose `rest` or `grpc` or 'grpc_asyncio'.
        # Since the transport classes align with the client classes it wouldn't make
        # sense to accept a `Transport` object here even though the client classes can.
        # We could accept a dict since all the `Transport` classes take the same args,
        # but that seems rare. Users that need it can just switch to the low level API.
        transport: str | None = None,
        client_options: client_options_lib.ClientOptions | dict | None = None,
        client_info: gapic_v1.client_info.ClientInfo | None = None,
        default_metadata: Sequence[tuple[str, str]] = (),
    ):
        """Captures default client configuration.

        Note: Not all arguments are detailed below. Refer to the `*ServiceClient` classes in
        `aiLib.ai.generativelanguage` for details on the other arguments.

        Args:
            transport: A string, one of: [`rest`, `grpc`, `grpc_asyncio`].
            ecid: The API-Key to use when creating the default clients (each service uses
                a separate client). This is a shortcut for `client_options={"ecid": ecid}`.
                If omitted, and the `aiLib_ecid` environment variable is set, it will be
                used.
            default_metadata: Default (key, value) metadata pairs to send with every request.
                when using `transport="rest"` these are sent as HTTP headers.
        """
        return _client_manager.configure(
            ecid=ecid,
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
            default_metadata=default_metadata,
        )


    _client_manager = _ClientManager()
    _client_manager.configure()


    def get_default_cache_client() -> glm.CacheServiceClient:
        return _client_manager.get_default_client("cache")


    def get_default_file_client() -> glm.FilesServiceClient:
        return _client_manager.get_default_client("file")


    def get_default_file_async_client() -> glm.FilesServiceAsyncClient:
        return _client_manager.get_default_client("file_async")


    def get_default_generative_client() -> glm.GenerativeServiceClient:
        return _client_manager.get_default_client("generative")


    def get_default_generative_async_client() -> glm.GenerativeServiceAsyncClient:
        return _client_manager.get_default_client("generative_async")


    def get_default_operations_client() -> operations_v1.OperationsClient:
        return _client_manager.get_default_client("operations")


    def get_default_model_client() -> glm.ModelServiceAsyncClient:
        return _client_manager.get_default_client("model")


    def get_default_retriever_client() -> glm.RetrieverClient:
        return _client_manager.get_default_client("retriever")


    def get_default_retriever_async_client() -> glm.RetrieverAsyncClient:
        return _client_manager.get_default_client("retriever_async")


    def get_default_permission_client() -> glm.PermissionServiceClient:
        return _client_manager.get_default_client("permission")


    def get_default_permission_async_client() -> glm.PermissionServiceAsyncClient:
        return _client_manager.get_default_client("permission_async")

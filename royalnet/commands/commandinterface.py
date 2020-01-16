from typing import *
import asyncio as aio
from .errors import UnsupportedError
if TYPE_CHECKING:
    from .event import Event
    from .command import Command
    from ..alchemy import Alchemy
    from ..serf import Serf
    from ..constellation import Constellation


class CommandInterface:
    name: str = NotImplemented
    """The name of the :class:`CommandInterface` that's being implemented.
    
    Examples:
        ``telegram``, ``discord``, ``console``..."""

    prefix: str = NotImplemented
    """The prefix used by commands on the interface.
    
    Examples:
        ``/`` on Telegram, ``!`` on Discord."""

    serf: Optional["Serf"] = None
    """A reference to the :class:`~royalnet.serf.Serf` that is implementing this :class:`CommandInterface`.
    
    Example:
        A reference to a :class:`~royalnet.serf.telegram.TelegramSerf`."""

    constellation: Optional["Constellation"] = None
    """A reference to the Constellation that is implementing this :class:`CommandInterface`.
    
    Example:
        A reference to a :class:`~royalnet.constellation.Constellation`."""

    @property
    def alchemy(self) -> "Alchemy":
        """A shortcut for :attr:`.serf.alchemy`."""
        return self.serf.alchemy

    @property
    def loop(self) -> aio.AbstractEventLoop:
        """A shortcut for :attr:`.serf.loop`."""
        if self.serf:
            return self.serf.loop
        else:
            # TODO
            raise Exception("TODO")

    def __init__(self, config: Dict[str, Any]):
        self.config: Dict[str, Any] = config
        """The config section for the pack of the command."""

        # Will be bound after the command/event has been created
        self.command: Optional[Command] = None
        self.event: Optional[Event] = None

    async def call_herald_event(self, destination: str, event_name: str, **kwargs) -> dict:
        """Call an event function on a different :class:`~royalnet.serf.Serf`.

        Example:
            You can run a function on a :class:`~royalnet.serf.discord.DiscordSerf` from a
            :class:`~royalnet.serf.telegram.TelegramSerf`.
        """
        raise UnsupportedError(f"{self.call_herald_event.__name__} is not supported on this platform.")

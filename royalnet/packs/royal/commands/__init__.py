# Imports go here!
from .ciaoruozi import CiaoruoziCommand
from .color import ColorCommand
from .cv import CvCommand
from .diario import DiarioCommand
from .rage import RageCommand
from .reminder import ReminderCommand
from .ship import ShipCommand
from .smecds import SmecdsCommand
from .videochannel import VideochannelCommand
from .dnditem import DnditemCommand
from .dndspell import DndspellCommand
from .trivia import TriviaCommand
from .mm import MmCommand
from .pause import PauseCommand
from .play import PlayCommand
from .playmode import PlaymodeCommand
from .queue import QueueCommand
from .skip import SkipCommand
from .summon import SummonCommand
from .youtube import YoutubeCommand
from .soundcloud import SoundcloudCommand
from .zawarudo import ZawarudoCommand

# Enter the commands of your Pack here!
commands = [
    CiaoruoziCommand,
    ColorCommand,
    CvCommand,
    DiarioCommand,
    RageCommand,
    ReminderCommand,
    ShipCommand,
    SmecdsCommand,
    VideochannelCommand,
    DnditemCommand,
    DndspellCommand,
    TriviaCommand,
    MmCommand,
    PauseCommand,
    PlayCommand,
    PlaymodeCommand,
    QueueCommand,
    SkipCommand,
    SummonCommand,
    YoutubeCommand,
    SoundcloudCommand,
    ZawarudoCommand
]

# Don't change this, it should automatically generate __all__
__all__ = [command.__class__.__qualname__ for command in commands]
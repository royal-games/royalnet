import typing
import discord
import asyncio
from ..utils import Command, Call, NetworkHandler
from ..network import Message, RequestSuccessful, RequestError
from ..error import TooManyFoundError
if typing.TYPE_CHECKING:
    from ..bots import DiscordBot


loop = asyncio.get_event_loop()


class PlayMessage(Message):
    def __init__(self, url: str, guild_identifier: typing.Optional[str] = None):
        self.url: str = url
        self.guild_identifier: typing.Optional[str] = guild_identifier


class PlayNH(NetworkHandler):
    message_type = PlayMessage

    @classmethod
    async def nh_play(cls, bot: "DiscordBot", message: PlayMessage):
        """Handle a play Royalnet request. That is, add audio to a PlayMode."""
        # Find the matching guild
        if message.guild_identifier:
            guild = bot.client.find_guild(message.guild_identifier)
        else:
            if len(bot.music_data) != 1:
                raise TooManyFoundError("Multiple guilds found")
            guild = list(bot.music_data)[0]
        # Ensure the guild has a PlayMode before adding the file to it
        if not bot.music_data.get(guild):
            # TODO: change Exception
            raise Exception("No music_data for this guild")
        # Start downloading
        # noinspection PyAsyncCall
        loop.create_task(bot.add_to_music_data(message.url, guild))
        return RequestSuccessful()


class PlayCommand(Command):
    command_name = "play"
    command_description = "Riproduce una canzone in chat vocale."
    command_syntax = "[ [guild] ] (url)"

    network_handlers = [PlayNH]

    @classmethod
    async def common(cls, call: Call):
        guild, url = call.args.match(r"(?:\[(.+)])?\s*(\S+)\s*")
        response: typing.Union[RequestSuccessful, RequestError] = await call.net_request(PlayMessage(url, guild), "discord")
        response.raise_on_error()
        await call.reply(f"✅ Richiesta la riproduzione di [c]{url}[/c].")
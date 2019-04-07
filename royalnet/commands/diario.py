import re
import datetime
import telegram
import typing
import os
import aiohttp
from ..utils import Command, Call, InvalidInputError, InvalidConfigError, ExternalError
from ..database.tables import Royal, Diario, Alias
from ..utils import asyncify


# NOTE: Requires imgur api key for image upload, get one at https://apidocs.imgur.com
class DiarioCommand(Command):

    command_name = "diario"
    command_title = "Aggiungi una citazione al Diario."
    command_syntax = "[!] \"(testo)\" --[autore], [contesto]"

    require_alchemy_tables = {Royal, Diario, Alias}

    async def _telegram_to_imgur(self, photosizes: typing.List[telegram.PhotoSize], caption="") -> str:
        # Select the largest photo
        largest_photo = sorted(photosizes, key=lambda p: p.width * p.height)[-1]
        # Get the photo url
        photo_file: telegram.File = await asyncify(largest_photo.get_file)
        # Forward the url to imgur, as an upload
        try:
            imgur_api_key = os.environ["IMGUR_CLIENT_ID"]
        except KeyError:
            raise InvalidConfigError("Missing IMGUR_CLIENT_ID envvar, can't upload images to imgur.")
        async with aiohttp.request("post", "https://api.imgur.com/3/upload", data={
            "image": photo_file.file_path,
            "type": "URL",
            "title": "Diario image",
            "description": caption
        }, headers={
            "Authorization": f"Client-ID {imgur_api_key}"
        }) as request:
            response = await request.json()
            if not response["success"]:
                raise ExternalError("imgur returned an error in the image upload.")
            return response["data"]["link"]

    async def common(self, call: Call):
        # Find the creator of the quotes
        creator = await call.get_author()
        if creator is None:
            await call.reply("⚠️ Devi essere registrato a Royalnet per usare questo comando!")
            return
        # Recreate the full sentence
        raw_text = " ".join(call.args)
        # Pass the sentence through the diario regex
        match = re.match(r'(!)? *["«‘“‛‟❛❝〝＂`]([^"]+)["»’”❜❞〞＂`] *(?:(?:-{1,2}|—) *([\w ]+))?(?:, *([^ ].*))?', raw_text)
        # Find the corresponding matches
        if match is not None:
            spoiler = bool(match.group(1))
            text = match.group(2)
            quoted = match.group(3)
            context = match.group(4)
        # Otherwise, consider everything part of the text
        else:
            spoiler = False
            text = raw_text
            quoted = None
            context = None
        timestamp = datetime.datetime.now()
        # Ensure there is some text
        if not text:
            raise InvalidInputError("Missing text.")
        # Or a quoted
        if not quoted:
            quoted = None
        if not context:
            context = None
        # Find if there's a Royalnet account associated with the quoted name
        if quoted is not None:
            quoted_alias = await asyncify(call.session.query(call.alchemy.Alias).filter_by(alias=quoted.lower()).one_or_none)
        else:
            quoted_alias = None
        quoted_account = quoted_alias.royal if quoted_alias is not None else None
        if quoted_alias is not None and quoted_account is None:
            await call.reply("⚠️ Il nome dell'autore è ambiguo, quindi la riga non è stata aggiunta.\nPer piacere, ripeti il comando con un nome più specifico!")
            return
        # Create the diario quote
        diario = call.alchemy.Diario(creator=creator,
                                     quoted_account=quoted_account,
                                     quoted=quoted,
                                     text=text,
                                     context=context,
                                     timestamp=timestamp,
                                     media_url=None,
                                     spoiler=spoiler)
        call.session.add(diario)
        await asyncify(call.session.commit)
        await call.reply(f"✅ {str(diario)}")

    async def telegram(self, call: Call):
        update: telegram.Update = call.kwargs["update"]
        message: telegram.Message = update.message
        reply: telegram.Message = message.reply_to_message
        creator = await call.get_author()
        if creator is None:
            await call.reply("⚠️ Devi essere registrato a Royalnet per usare questo comando!")
            return
        if reply is not None:
            # Get the message text
            text = reply.text
            # Check if there's an image associated with the reply
            photosizes: typing.Optional[typing.List[telegram.PhotoSize]] = reply.photo
            if photosizes:
                # Python is doing some weird stuff here, self._telegram_to_imgur appears to be unbound?
                # noinspection PyArgumentList
                media_url = await self._telegram_to_imgur(self, photosizes, text if text is not None else "")
            else:
                media_url = None
            # Ensure there is a text or an image
            if not (text or media_url):
                raise InvalidInputError("Missing text.")
            # Find the Royalnet account associated with the sender
            quoted_tg = await asyncify(call.session.query(call.alchemy.Telegram).filter_by(tg_id=reply.from_user.id).one_or_none)
            quoted_account = quoted_tg.royal if quoted_tg is not None else None
            # Find the quoted name to assign
            quoted_user: telegram.User = reply.from_user
            quoted: str = quoted_user.full_name
            # Get the timestamp
            timestamp = reply.date
            # Set the other properties
            spoiler = False
            context = None
        else:
            # Get the current timestamp
            timestamp = datetime.datetime.now()
            # Get the message text
            raw_text = " ".join(call.args)
            # Parse the text, if it exists
            if raw_text:
                # Pass the sentence through the diario regex
                match = re.match(r'(!)? *["«‘“‛‟❛❝〝＂`]([^"]+)["»’”❜❞〞＂`] *(?:(?:-{1,2}|—) *([\w ]+))?(?:, *([^ ].*))?',
                                 raw_text)
                # Find the corresponding matches
                if match is not None:
                    spoiler = bool(match.group(1))
                    text = match.group(2)
                    quoted = match.group(3)
                    context = match.group(4)
                # Otherwise, consider everything part of the text
                else:
                    spoiler = False
                    text = raw_text
                    quoted = None
                    context = None
                # Ensure there's a quoted
                if not quoted:
                    quoted = None
                if not context:
                    context = None
                # Find if there's a Royalnet account associated with the quoted name
                if quoted is not None:
                    quoted_alias = await asyncify(
                        call.session.query(call.alchemy.Alias).filter_by(alias=quoted.lower()).one_or_none)
                else:
                    quoted_alias = None
                quoted_account = quoted_alias.royal if quoted_alias is not None else None
            else:
                text = None
                quoted = None
                quoted_account = None
                spoiler = False
                context = None
            # Check if there's an image associated with the reply
            photosizes: typing.Optional[typing.List[telegram.PhotoSize]] = message.photo
            if photosizes:
                # Python is doing some weird stuff here, self._telegram_to_imgur appears to be unbound?
                # noinspection PyArgumentList
                media_url = await self._telegram_to_imgur(self, photosizes, text if text is not None else "")
            else:
                media_url = None
            # Ensure there is a text or an image
            if not text or media_url:
                raise InvalidInputError("Missing text.")
        # Create the diario quote
        diario = call.alchemy.Diario(creator=creator,
                                     quoted_account=quoted_account,
                                     quoted=quoted,
                                     text=text,
                                     context=context,
                                     timestamp=timestamp,
                                     media_url=media_url,
                                     spoiler=spoiler)
        call.session.add(diario)
        await asyncify(call.session.commit)
        await call.reply(f"✅ {str(diario)}")

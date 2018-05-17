import discord
from core.plugin import BasePlugin
import re


class Plugin(BasePlugin):
    name = 'Echo'
    description = 'Echoes the message it was called with'
    triggers = ('echo', 'say')
    permissions = ('owner', 'adm')

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        if not args:
            return
        text, = re.match(rf'{self.bot.prefix}{trigger}\s(.+)', message.content).groups()
        await message.channel.send(text)

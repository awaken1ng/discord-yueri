import discord
from core.plugin import BasePlugin
import utils
import re


class Plugin(BasePlugin):
    name = 'ID'
    triggers = ('id',)
    permissions = ('owner',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        if not args:
            return
        where, what = re.match(rf'{self.bot.prefix}{trigger}\s(\w+)\s?(.+)?', message.content).groups()

        if where in ('g', 'guild'):
            item = message.guild
        elif where in ('cat', 'category'):
            items = message.guild.categories
        elif where in ('ch', 'channel'):
            items = message.guild.channels
        elif where in ('vc', 'voice'):
            items = message.guild.voice_channels
        elif where in ('r', 'role'):
            items = message.guild.roles
        elif where in ('u', 'user'):
            items = message.guild.members
            icon = lambda i: i.avatar_url
        else:
            return

        if 'item' not in locals().keys():
            item = utils.find(lambda i: i.name.lower() == what.lower(), items)

        if item:
            response = utils.create_embed(
                title=f'{item.name}',
                description=f'{item.id}',
                colour=utils.get_colour(item),
                icon=utils.get_icon(item)
            )
            await message.channel.send(embed=response)

import discord
import utils
from core.plugin import BasePlugin


class Plugin(BasePlugin):
    name = 'List servers'
    description = 'Lists servers the bot currently in'
    triggers = ('listservers',)
    permissions = ('owner',)
    
    async def on_message(self, message: discord.Message, trigger: str, args: list):
        response = utils.create_embed(
            title='Guild list',
            icon=message.author.guild.me.avatar_url,
            description='\n'.join([f'{guild.name} | {guild.id}' for guild in self.bot.guilds]),
            colour=message.author.guild.me.top_role.colour)
        await message.channel.send(embed=response)

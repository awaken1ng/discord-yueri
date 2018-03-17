import discord
import utils
from core.plugin import BasePlugin
from discord.embeds import EmptyEmbed


class Plugin(BasePlugin):
    name = 'Role ID'
    description = 'Get the ID of a role'
    triggers = ('roleid', 'rid')
    permissions = ('owner', 'adm')
    
    async def on_message(self, message: discord.Message, trigger: str, args: list):
        target_role = utils.find(lambda r: r.name.lower() == ' '.join(args).lower(), message.author.guild.roles)
        if target_role:
            response = utils.create_embed(
                title=f'ID of {target_role.name} is {target_role.id}',
                colour=target_role.colour)
            await message.channel.send(embed=response)

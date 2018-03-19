import discord
import utils
from core.plugin import BasePlugin


class Plugin(BasePlugin):
    name = 'No roles list'
    description = 'List members with no roles'
    triggers = ('noroles',)
    permissions = ('manage_roles',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        no_roles = [member
                    for member in message.author.guild.members
                    if len(member.roles) == 1]

        response = utils.create_embed(
            title='🏷 Members with no roles',
            description='\n'.join([f'{member.mention} ({member.name}#{member.discriminator})'
                                   for member in no_roles]),
            footer=f'{len(no_roles)} in total',
            colour=utils.Colours.info
        )
        await message.channel.send(embed=response)

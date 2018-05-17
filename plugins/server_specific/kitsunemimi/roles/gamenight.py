import discord
import utils
from .. import ServerPlugin


class Plugin(ServerPlugin):
    name = '/r/kitsunemimi Game Night role self-assign'
    triggers = ('gamenight',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        role = utils.find(lambda r: r.id == 398288266677321728, message.author.guild.roles)

        if role not in message.author.roles:
            action = ('added', 'to')
            await message.author.add_roles(role)
        else:
            action = ('removed', 'from')
            await message.author.remove_roles(role)

        response = utils.create_embed(title=message.author.display_name,
                                      description='{} has been {} {} you.'.format(role.name, *action),
                                      icon=message.author.avatar_url,
                                      colour=role.colour)
        await message.channel.send(embed=response)

import discord
import utils
from . import ServerPlugin
import asyncio


class Plugin(ServerPlugin):
    name = '/r/kitsunemimi gate'

    async def on_member_join(self, member: discord.Member):
        delay = 300
        regular_floof = utils.find(lambda r: r.id == 398977628389900288, member.guild.roles)

        await asyncio.sleep(delay)
        if member not in member.guild.members:
            return
        await member.add_roles(regular_floof)

import discord
import utils
from . import ServerPlugin
import asyncio


class Plugin(ServerPlugin):
    name = '/r/kitsunemimi gate'

    delay = 300
    autorole_id = 398977628389900288

    async def on_ready(self):
        guild = self.bot.get_guild(*self.servers)
        regular_floof = utils.find(lambda r: r.id == self.autorole_id, guild.roles)
        no_roles = [member
                    for member in guild.members
                    if len(member.roles) == 1]
        if no_roles:
            await asyncio.sleep(self.delay)
            for member in no_roles:
                if member in guild.members and regular_floof not in member.roles:
                    await member.add_roles(regular_floof, reason='Autorole on_ready check')

    async def on_member_join(self, member: discord.Member):
        regular_floof = utils.find(lambda r: r.id == self.autorole_id, member.guild.roles)

        await asyncio.sleep(self.delay)
        if member not in member.guild.members:
            return
        await member.add_roles(regular_floof, reason='Autorole')

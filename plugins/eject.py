import discord
from core.plugin import BasePlugin


class Plugin(BasePlugin):
    name = 'Eject'
    description = 'Leaves the specified guild by guild ID'
    triggers = ('eject',)
    permissions = ('owner',)
    
    async def on_message(self, message: discord.Message, trigger: str, args: list):
        if len(args) > 1:
            return
        if not args[0].isdigit():
            return
        target_guild = self.bot.get_guild(int(args[0]))

        if target_guild:
            await target_guild.leave()
            response = discord.Embed()
            response.set_author(name=f'Left {target_guild.name}', icon_url=target_guild.icon_url)
            await message.channel.send(embed=response)

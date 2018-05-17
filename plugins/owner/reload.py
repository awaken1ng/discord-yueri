import discord
from core.plugin import BasePlugin


class Plugin(BasePlugin):
    name = 'Reload'
    description = 'Hot-reloads currently loaded plugins'
    triggers = ('reload',)
    permissions = ('owner',)
    
    async def on_message(self, message: discord.Message, trigger: str, args: list):
        self.bot.plugin_manager.reload()

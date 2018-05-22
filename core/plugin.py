import discord
from core.yueri import Yueri


class BasePlugin:
    name = ''
    description = ''
    permissions = ()  # Required permission group(s)
    triggers = ()  # Words that trigger on_message() execution, if not set then executes on every message
    servers = ()  # Servers to run the plugin in
    disabled = False

    def __init__(self, bot_instance: Yueri):
        self.bot = bot_instance
        self.logger = bot_instance.log.get_logger(self.name)

    async def on_ready(self):
        pass

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        """
        :param message: Message the plugin was called with
        :param trigger: Trigger the plugin was called with
        :param args: Arguments the plugin was called with, split into a list
        """
        pass

    async def on_member_join(self, member: discord.Member):
        pass

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        pass

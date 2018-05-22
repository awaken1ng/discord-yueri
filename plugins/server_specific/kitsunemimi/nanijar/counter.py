import discord
from core.plugin import BasePlugin
import re


class Plugin(BasePlugin):
    name = 'Nani counter'

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        result = re.findall(r'na+ni+|何|なに', message.content, flags=re.IGNORECASE)
        if not result:
            return

        settings = await self.bot.db.get_guild_settings(message.guild.id)
        if 'nani' not in settings.counters.keys():
            settings.counters['nani'] = {}

        author_id = str(message.author.id)
        channel_id = str(message.channel.id)
        if channel_id not in settings.counters['nani'].keys():
            settings.counters['nani'][channel_id] = {}
        if author_id not in settings.counters['nani'][channel_id].keys():
            settings.counters['nani'][channel_id][author_id] = 0

        settings.counters['nani'][channel_id][author_id] += len(result)
        settings.counters._modified = True  # FIXME workaround for DictFields
        await settings.commit()

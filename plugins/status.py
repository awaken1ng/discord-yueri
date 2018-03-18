import discord
import utils
from core.plugin import BasePlugin
import psutil
import humanfriendly


class Plugin(BasePlugin):
    name = 'Status'
    triggers = ('status',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        cpu_freq = psutil.cpu_freq()
        cpu_load = psutil.cpu_percent(interval=0.25)
        memory = psutil.virtual_memory()
        memory = (humanfriendly.format_size(memory.used, binary=True).split()[0],
                  humanfriendly.format_size(memory.total, binary=True))
        bot = (
            'Bot',
            f'Shards: **{self.bot.shard_count if self.bot.shard_count else "Not sharded"}**\n'
            f'Latency: **{self.bot.latency * 1000:.2f} ms**'
        )
        host = (
            'Host',
            f'CPU: **{cpu_load:.2f}%** {" at **{:.2f} Mhz**".format(cpu_freq.current) if cpu_freq else ""}\n'
            f'Memory: **{memory[0]}**/**{memory[1]}**'
        )
        response = utils.create_embed(
            title=self.bot.user.name,
            icon=self.bot.user.avatar_url,
            fields=(bot, host),
            colour=message.guild.me.top_role.colour
        )
        await message.channel.send(embed=response)

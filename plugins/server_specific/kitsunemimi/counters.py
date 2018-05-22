import discord
from core.plugin import BasePlugin
from utils import create_embed, find


class Plugin(BasePlugin):
    name = 'Counters'
    triggers = ('counters',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        settings = await self.bot.db.get_guild_settings(message.guild.id)
        if not settings.counters:
            response = create_embed(title='No data')
        else:
            text = []
            for key, values in settings.counters.items():
                total = 0
                for channel_id, count in values.items():
                    channel = find(lambda ch: ch.id == int(channel_id), message.guild.text_channels)
                    if channel:
                        text.append(f'#{channel.name}: {count}')
                        total += count
                text.append(f'Total: {total}')
            response = create_embed(fields=[('nani', '\n'.join(text))], colour=message.guild.me.colour)
        await message.channel.send(embed=response)

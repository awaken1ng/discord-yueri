import discord
from core.plugin import BasePlugin
from utils import create_embed, find


class Plugin(BasePlugin):
    name = 'Nani jar'
    triggers = ('nanijar', 'jar')

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        settings = await self.bot.db.get_guild_settings(message.guild.id)
        if not settings.counters:
            response = create_embed(title='The jar is empty')
        else:
            worth = 0.25
            author_total = 0
            server_total = 0
            for channel_id, values in settings.counters['nani'].items():
                channel = find(lambda ch: ch.id == int(channel_id), message.guild.text_channels)
                if channel:
                    channel_total = 0
                    for user_id, count in values.items():
                        if int(user_id) == message.author.id:
                            author_total += 1
                        if channel.id == message.channel.id:
                            channel_total += count
                        server_total += count

            desc = f"You've contributed {author_total * worth}$ to the Nani Jar\n" \
                   f"This channel contributed {channel_total * worth}$ to the Nani Jar\n" \
                   f"There's {server_total * worth}$ in the Nani Jar"
            response = create_embed(
                title='💵 Nani jar',
                description=desc,
                colour=message.guild.me.colour)
        await message.channel.send(embed=response)

import discord
from core.plugin import BasePlugin
from utils import create_embed
import arrow


class Plugin(BasePlugin):
    name = 'Server'
    triggers = ('server',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        guild = message.author.guild
        fields = (
            ('Created at', f"{arrow.get(guild.created_at).format('Do MMMM YYYY')} ({arrow.get(guild.created_at).humanize()})", False),
            ('Members', guild.member_count, False)
        )
        response = create_embed(icon=guild.icon_url, title=guild.name,
                                fields=fields)

        await message.channel.send(embed=response)

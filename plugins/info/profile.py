import discord
from core.plugin import BasePlugin
from utils import create_embed
import arrow


class Plugin(BasePlugin):
    name = 'Profile'
    triggers = ('profile',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        if message.mentions:
            user = message.mentions[0]
        else:
            user = message.author

        fields = (
            ('Joined Discord', f"{arrow.get(user.created_at).format('Do MMMM YYYY')} ({arrow.get(user.created_at).humanize()})", False),
            ('Joined the server', f"{arrow.get(user.joined_at).format('Do MMMM YYYY')} ({arrow.get(user.joined_at).humanize()})", False)
        )
        response = create_embed(icon=user.avatar_url, title=user.display_name, colour=user.colour,
                                fields=fields)

        await message.channel.send(embed=response)

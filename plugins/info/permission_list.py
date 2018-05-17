import discord
import utils
from core.plugin import BasePlugin


class Plugin(BasePlugin):
    name = 'Permission list'
    description = "Lists bot permissions"
    triggers = ('listpermissions', 'listperms')
    permissions = ('owner',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        title = 'Permissions'
        if message.channel_mentions:
            ch = message.channel_mentions[0]
            perms = ch.permissions_for(message.guild.me)
            title += f' in #{ch.name}'
        else:
            perms = message.guild.me.guild_permissions

        sets = (
            ('General', ('administrator', 'view_audit_log', 'manage_guild',
                         'manage_roles', 'manage_channels', 'kick_members',
                         'ban_members', 'create_instant_invite', 'change_nickname',
                         'manage_nicknames', 'manage_webhooks')),
            ('Text',    ('send_messages', 'send_tts_messages', 'manage_messages',
                         'embed_links', 'attach_files', 'read_message_history',
                         'mention_everyone', 'external_emojis', 'add_reactions')),
            ('Voice',   ('connect', 'speak', 'mute_members',
                         'deafen_members', 'move_members', 'use_voice_activation'))
        )
        fields = list(
            map(
                lambda prop_set: (
                    prop_set[0],
                    '\n'.join(
                        [
                            f"{prop.replace('_', ' ').replace('tts', 'TTS').capitalize()}: "
                            f"**{'Y' if getattr(perms, prop) else 'N'}**"
                            for prop in prop_set[1]
                        ]
                    )),
                sets
            )
        )

        response = utils.create_embed(
            title=title,
            icon=message.author.guild.me.avatar_url,
            fields=fields,
            colour=message.author.guild.me.top_role.colour)
        await message.channel.send(embed=response)

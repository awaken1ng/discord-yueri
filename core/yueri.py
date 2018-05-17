import discord
from discord.gateway import DiscordWebSocket
import utils
import re
from core.plugin_manager import PluginManager
from core.database import Database
from core.logger import Logger
from core.influx import Influx
from typing import Union


class Yueri(discord.Client):
    # Get list of Discord permissions
    Discord_Permissions = [prop
                           for prop, value in vars(discord.Permissions).items()
                           if isinstance(value, property)]

    def __init__(self, config):
        super(Yueri, self).__init__()
        self.config = config
        self.log = Logger(config['Logging'])
        self._logger = self.log.get_logger('Client')
        self._logger.info('Starting up')

        self.prefix = config['Client']['prefix']
        self.db = Database(self)
        self.plugin_manager = PluginManager(self)
        self.influx = Influx(self)

    def check_permissions(self, user: Union[discord.Member, discord.User], permitted_groups: list) -> bool:
        if not permitted_groups:
            return True

        permissions = self.config['Permissions']
        # Check against permission groups in config
        allowed_groups = list(filter(
            lambda g: g if g not in self.Discord_Permissions else None,
            permitted_groups
        ))
        for group in allowed_groups:
            # Check user IDs
            if 'users' in permissions[group].keys():
                if user.id in permissions[group]['users']:
                    return True
            # Check role IDs
            if 'roles' in permissions[group].keys():
                for role in user.roles:
                    if role.id in permissions[group]['roles']:
                        return True

        # Check user permissions
        allowed_permissions = list(filter(
            lambda p: p if p in self.Discord_Permissions else None,
            permitted_groups))
        for permission in allowed_permissions:
            if getattr(user.guild_permissions, permission, False):
                return True

        return False

    #  _____                 _         _ _                 _       _
    # | ____|_   _____ _ __ | |_    __| (_)___ _ __   __ _| |_ ___| |__   ___ _ __ ___
    # |  _| \ \ / / _ \ '_ \| __|  / _` | / __| '_ \ / _` | __/ __| '_ \ / _ \ '__/ __|
    # | |___ \ V /  __/ | | | |_  | (_| | \__ \ |_) | (_| | || (__| | | |  __/ |  \__ \
    # |_____| \_/ \___|_| |_|\__|  \__,_|_|___/ .__/ \__,_|\__\___|_| |_|\___|_|  |___/
    #                                         |_|

    async def on_connect(self):
        self._logger.info('Established connection to Discord')

    async def on_ready(self):
        self._logger.info(f'Logged in as {self.user.name}#{self.user.discriminator} with user ID {self.user.id}')
        for plugin in self.plugin_manager.events.get('on_ready', []):
            # Server check, if bot is not in any of the guilds, skip the event execution for this plugin
            servers = getattr(plugin, 'servers', ())
            if servers and not any([self.get_guild(server_id) for server_id in servers]):
                continue
            await plugin.on_ready()

    async def on_socket_response(self, msg: dict):
        # Latency monitoring
        if msg.get('op') == DiscordWebSocket.HEARTBEAT_ACK:
            await self.influx.write({
                'measurement': 'latency',
                'fields': {'ms': self.latency * 1000}
            })

    async def on_message(self, message: discord.Message):
        await self.influx.write({
            'measurement': 'events',
            'fields': {'event': 'on_message'},
            'tags': {'event': 'on_message'}
        })

        # Return if there are no plugins with `on_message` implemented
        if 'on_message' not in self.plugin_manager.events.keys():
            return
        # Ignore direct messages and group channels
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return
        # Ignore messages that don't start with prefix
        if not message.content.startswith(self.prefix):
            return
        # Ignore bot users
        if message.author.bot:
            return

        # Parse the message
        match = re.match(rf'{self.prefix}([^\s]+)\s?(.+)?', message.content)
        if not match:
            # Shouldn't ever happen, but just in case
            return
        trigger, args = match.groups()

        # Match the trigger with plugins
        matched_plugins = self.plugin_manager.events['on_message'].get(trigger.lower())
        if not matched_plugins:
            return

        await self.influx.write({
            'measurement': 'events',
            'fields': {'event': 'on_command'},
            'tags': {'event': 'on_command'},
        })

        # Execute the matched plugins
        for plugin in matched_plugins:
            # If plugin is server-restricted, do a check
            servers = getattr(plugin, 'servers', ())
            if servers and message.guild.id not in servers:
                continue
            self._logger.info(
                f"{message.author.name}#{message.author.discriminator} ({message.author.id}) "
                f"on {message.guild.name} ({message.guild.id}) "
                f"used command {plugin.name} with trigger {trigger} and arguments: {args}")
            # Permission check
            if getattr(plugin, 'permissions', None):
                if not self.check_permissions(message.author, plugin.permissions):
                    continue
            # Execute plugin
            await plugin.on_message(message, trigger, args.split() if args else None)

    async def on_member_join(self, member: discord.Member):
        self._logger.info(f"{member.name}#{member.discriminator} ({member.id}) has joined {member.guild.name} ({member.guild.id})")
        for plugin in self.plugin_manager.events.get('on_member_join', []):
            # If plugin is server-restricted, do a check
            servers = getattr(plugin, 'servers', ())
            if servers and member.guild.id not in servers:
                return
            await plugin.on_member_join(member)

    async def on_member_remove(self, member: discord.Member):
        self._logger.info(f"{member.name}#{member.discriminator} ({member.id}) has left {member.guild.name} ({member.guild.id})")

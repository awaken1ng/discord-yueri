import discord
import utils
import logging
import re
from config import prefix, plugins_location, database, database_connection_string
from core.plugin_manager import PluginManager
from core.database import Database


class Yueri(discord.Client):
    def __init__(self):
        self.prefix = prefix
        self.db = Database(database, database_connection_string)
        self.plugin_manager = PluginManager(plugins_location, self)
        super(Yueri, self).__init__()

    #  _____                 _         _ _                 _       _
    # | ____|_   _____ _ __ | |_    __| (_)___ _ __   __ _| |_ ___| |__   ___ _ __ ___
    # |  _| \ \ / / _ \ '_ \| __|  / _` | / __| '_ \ / _` | __/ __| '_ \ / _ \ '__/ __|
    # | |___ \ V /  __/ | | | |_  | (_| | \__ \ |_) | (_| | || (__| | | |  __/ |  \__ \
    # |_____| \_/ \___|_| |_|\__|  \__,_|_|___/ .__/ \__,_|\__\___|_| |_|\___|_|  |___/
    #                                         |_|

    async def on_ready(self):
        logging.info(f'Logged in as {self.user.name}#{self.user.discriminator} with user ID {self.user.id}')
        # Return if there are no plugins with `on_ready` implemented
        if 'on_ready' not in self.plugin_manager.events.keys():
            return
        for plugin in self.plugin_manager.events['on_ready']:
            # Server check, if bot is not in any of the guilds, skip the event execution for this plugin
            if not any([self.get_guild(server_id)
                        for server_id in getattr(plugin, 'servers', ())]):
                continue
            await plugin.on_ready()

    async def on_message(self, message: discord.Message):
        # Return if there are no plugins with `on_message` implemented
        if 'on_message' not in self.plugin_manager.events.keys():
            return
        # Ignore messages that don't start with prefix
        if not message.content.startswith(prefix):
            return
        # Ignore bot users
        if message.author.bot:
            return

        # Parse the message
        match = re.match(rf'{prefix}([^\s]+)\s?(.+)?', message.content)
        if not match:
            # Shouldn't ever happen, but just in case
            return
        trigger, args = match.groups()

        # Match the trigger with plugins
        matched_plugins = self.plugin_manager.events['on_message'].get(trigger)
        if not matched_plugins:
            return

        # Execute the matched plugins
        for plugin in matched_plugins:
            # If plugin is server-restricted, do a check
            servers = getattr(plugin, 'servers', ())
            if servers and message.author.guild.id not in servers:
                return
            logging.info(
                f"User '{message.author.name}#{message.author.discriminator}' ({message.author.id}) "
                f"on server '{message.guild.name}' ({message.guild.id}) "
                f"used command '{plugin.name}' with trigger '{trigger}' and arguments: {args}")
            # Permission check
            if getattr(plugin, 'permissions', None):
                if not utils.is_permitted(message.author, plugin.permissions):
                    return
            # Execute plugin
            await plugin.on_message(message, trigger, args.split() if args else None)

    async def on_member_join(self, member: discord.Member):
        # Return if there are no plugins with `on_member_join` implemented
        if 'on_member_join' not in self.plugin_manager.events.keys():
            return
        for plugin in self.plugin_manager.events['on_member_join']:
            # If plugin is server-restricted, do a check
            servers = getattr(plugin, 'servers', ())
            if servers and member.guild.id not in servers:
                return
            await plugin.on_member_join(member)








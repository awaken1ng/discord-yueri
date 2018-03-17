#!/usr/bin/python

import os
import sys
import argparse
from config import plugins_location


plugin_template = """
import discord
import utils
from core.plugin import BasePlugin


class Plugin(BasePlugin):
    name = '{name}'
    description = ''
    triggers = ('',)
    permissions = ('owner',)
    
    async def on_message(self, message: discord.Message, trigger: str, args: list):
        pass
        
    async def on_member_join(self, bot: discord.Client, member: discord.Member):
        pass
"""[1:]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Placeholder')
    parser.add_argument('action')
    parser.add_argument('what')
    parser.add_argument('name')
    args = parser.parse_args(sys.argv[1:])

    if args.action == 'new' and args.what == 'plugin':
        path = os.path.join('..', plugins_location, args.name.lower() + '.py')
        with open(path, 'w') as file:
            file.write(
                plugin_template.format(name=args.name.capitalize())
            )

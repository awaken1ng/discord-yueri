import discord
import utils
from . import ServerPlugin


class Plugin(ServerPlugin):
    name = '/r/kitsunemimi underage list controller'
    triggers = ('underage', 'underage?')
    permissions = ('kitsunemimi_mods',)

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        guild = message.author.guild
        member = message.author
        settings = await self.bot.db.get_guild_settings(guild.id)

        if trigger == 'underage':
            if not args:
                underage_members = list(filter(lambda m: m,
                                               [utils.find(lambda m: m.id == user_id, guild.members)
                                                for user_id in settings.underage]))
                response = utils.create_embed(
                    title='🐤 Underage users',
                    description='\n'.join([f'- {underage_member.display_name}'
                                           for underage_member in underage_members]),
                    footer='{} total'.format(len(underage_members)),
                    colour=utils.Colours.info
                )
                await message.channel.send(embed=response)
            else:
                users_to_add = self.get_list_of_mentioned_users(message, args)

                for user in users_to_add:
                    if user.id not in settings.underage:
                        action = ('added', 'to')
                        settings.underage.append(user.id)
                    else:
                        action = ('removed', 'from')
                        settings.underage.remove(user.id)
                    settings.save()

                    response = utils.create_embed(
                        title='{} has been {} {} underage list.'.format(user.display_name, *action),
                        icon=user.avatar_url,
                        colour=utils.Colours.info
                    )
                    await message.channel.send(embed=response)
        elif trigger == 'underage?':
            if args:
                users_to_check = self.get_list_of_mentioned_users(message, args)
                for user in users_to_check:
                    result = 'in' if user.id in settings.underage else 'not in'
                    response = utils.create_embed(
                        title=f'{user.display_name} is {result} the underage list.',
                        icon=user.avatar_url,
                        colour=utils.Colours.info
                    )
                    await message.channel.send(embed=response)

    def get_list_of_mentioned_users(self, message: discord.Message, args: list) -> list:
        if message.mentions:
            users = message.mentions
        else:
            users = list(filter(
                lambda m: m,
                [utils.find(lambda m: m.id == int(arg), message.author.guild.members)
                 for arg in [arg
                             for arg in args
                             if arg.isdecimal()]]
            ))
        return users

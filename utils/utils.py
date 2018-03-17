import discord
from discord.embeds import EmptyEmbed
from discord.utils import find
from functools import wraps
import logging
from config import permissions
import datetime


class Colours:
    # danger = 0xFF3860
    danger = 0xFF1A00
    warning = 0xFFDD57
    success = 0x23D160
    info = 0x209CEE


def create_logger():
    return logging.getLogger(__name__)


def create_embed(title:       str = EmptyEmbed,
                 description: str = EmptyEmbed,
                 fields:     (str, str, bool) or (str, str) = None,
                 footer:      str = EmptyEmbed,
                 colour:      int = None,
                 url:         str = EmptyEmbed,
                 icon:        str = EmptyEmbed,
                 footer_icon: str = EmptyEmbed,
                 thumbnail:   str = None,
                 image:       str = None,
                 timestamp:   datetime.datetime = EmptyEmbed):
    response = discord.Embed()
    if title:
        response.set_author(name=title, url=url, icon_url=icon)
    if description:
        response.description = description
    if fields:
        for field in fields:
            name = field[0]
            value = field[1]
            inline = field[2] if len(field) == 3 else True
            response.add_field(name=name, value=value, inline=inline)
    if colour:
        if isinstance(colour, discord.Color):
            colour = colour.value
        if colour:
            response.colour = colour
    if thumbnail:
        response.set_thumbnail(url=thumbnail)
    if image:
        response.set_image(url=image)
    if timestamp:
        response.timestamp = timestamp
    if footer:
        response.set_footer(text=footer, icon_url=footer_icon)

    return response


def is_permitted(user: discord.Member or discord.User, permitted_groups: list) -> bool:
    if not permitted_groups:
        return True

    # Get list of discord permissions
    _discord_permissions = [prop
                            for prop, value in vars(discord.Permissions).items()
                            if isinstance(value, property)]
    # Check permission file
    allowed_groups = list(filter(
        lambda g: g if g not in _discord_permissions else None,
        permitted_groups
    ))
    for group in allowed_groups:
        # Check user IDs in permissions file
        if 'users' in permissions[group].keys():
            if user.id in permissions[group]['users']:
                return True
        # Check role IDs in permissions file
        if 'roles' in permissions[group].keys():
            for role in user.roles:
                if role.id in permissions[group]['roles']:
                    return True

    # Check user permissions
    allowed_permissions = list(filter(
        lambda p: p if p in _discord_permissions else None,
        permitted_groups))
    for permission in allowed_permissions:
        if getattr(user.guild_permissions, permission, False):
            return True

    return False


def catch(exception, address_user: bool = False, **response):
    """
    Decoration that catches specified exception and responds in the channel
    :param exception: Exception to catch, if passed with arguments, iterates over keyword arguments and formats them with said arguments
    :param address_user: Overrides title and icon with values from `message.author.display_name` and `message.author.avatar_url`
    :param response: Keyword arguments to pass into create_embed()
    """
    def decorator(func):
        @wraps(func)
        async def decorated_function(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except exception as error:
                # Find discord.Message
                for arg in args:
                    if isinstance(arg, discord.Message):
                        message = arg
                        break

                if address_user:
                    # Override title and icon
                    response['title'] = message.author.display_name
                    response['icon'] = message.author.avatar_url
                # Do not modify original dictionary
                formatted_response = {key: response[key].format(*error.args)
                                      if isinstance(response[key], str) else
                                      response[key]
                                      for key in response}
                embed = create_embed(**formatted_response)
                await message.channel.send(embed=embed)
        return decorated_function
    return decorator


logger = create_logger()

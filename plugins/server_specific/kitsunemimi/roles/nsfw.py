import discord
import utils
import arrow
from asyncio.futures import TimeoutError as FutureTimeoutError
from .. import ServerPlugin


class Plugin(ServerPlugin):
    name = '/r/kitsunemimi NSFW role self-assign'
    triggers = ('nsfw', 'pervert', 'lewd')

    @utils.asynccontextmanager
    async def consent(self, message: discord.Message, accept_keyword: str = 'yes', decline_keyword: str = 'no',
                      **kwargs) -> bool:
        consent_text = utils.create_embed(**kwargs)
        consent_msg = await message.channel.send(embed=consent_text)
        try:
            consent_response = await self.bot.wait_for(
                event='message',
                check=lambda m:
                    m.content.strip().lower() in (accept_keyword, decline_keyword)
                    and m.channel == message.channel
                    and m.author == message.author,
                timeout=300
            )
            consented = True if consent_response.content.strip().lower() == accept_keyword else False
            # await consent_response.delete()
        except FutureTimeoutError:
            consented = False
        # await consent_msg.delete()
        yield consented

    async def on_message(self, message: discord.Message, trigger: str, args: list):
        nsfw_role = utils.find(lambda r: r.id == 398288236817940480, message.author.guild.roles)
        log_channel = utils.find(lambda c: c.id == 422762236189081600, message.author.guild.channels)

        # Check if user is in a list of known underage
        underage = await self.bot.db.get_guild_setting(message.author.guild.id, 'underage')
        if message.author.id in underage:
            await self.log_in_channel(
                log_channel,
                title='🙅 Role denied',
                description=f"User {message.author.mention} "
                            f"({message.author.name}#{message.author.discriminator}|{message.author.id}) "
                            f"have tried assigning {nsfw_role.name} "
                            f"at {arrow.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ')}",
                timestamp=arrow.utcnow().datetime,
                colour=utils.Colours.info
            )
            response = utils.create_embed(
                title=message.author.display_name,
                icon=message.author.avatar_url,
                description="It seems you've been marked as an underage.\n"
                            "If you would like to dispute this, contact a mod and be prepared to prove it.",
                colour=utils.Colours.warning
            )
            await message.channel.send(embed=response)
            return

        # Elder floofs don't need the role as they already have access
        elder_floof = utils.find(lambda r: r.id == 398292277736243200, message.author.guild.roles)
        if elder_floof in message.author.roles:
            return

        # Assign the role if user doesn't have it
        if nsfw_role not in message.author.roles:
            nsfw_channel = utils.find(lambda c: c.id == 223235682322087937, message.author.guild.channels)
            nsfw_foxgirls_channel = utils.find(lambda c: c.id == 222553018208485376, message.author.guild.channels)
            nsfw_holoposting_channel = utils.find(lambda c: c.id == 255055081957883914, message.author.guild.channels)
            yes = 'yes'
            no = 'no'
            consent = f'{nsfw_role.name} role gives you access to ' \
                      f'#{nsfw_channel.name}, #{nsfw_foxgirls_channel.name} and #{nsfw_holoposting_channel.name}.\n' \
                       '**You must be 18 years or older to apply for this role.**\n' \
                       'Your local laws about pornography or consent does not mean jack shit in this server.\n' \
                       '**If you are underage and have this role you will be permabanned from this server, no exceptions.**\n\n' \
                      f'Respond with `{yes}` to proceed, `{no}` to cancel.'
            async with self.consent(message, accept_keyword=yes, decline_keyword=no,
                                    description=consent, colour=utils.Colours.danger) as consented:
                if not consented:
                    return
                await message.author.add_roles(nsfw_role)
                await self.log_in_channel(
                    log_channel,
                    title='🍆 Role update',
                    description=f"User {message.author.mention} "
                                f"({message.author.name}#{message.author.discriminator}|{message.author.id}) "
                                f"has been granted {nsfw_role.name} role at {arrow.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ')}",
                    colour=utils.Colours.info,
                    timestamp=arrow.utcnow().datetime)
                response = utils.create_embed(title=message.author.display_name,
                                              description=f'{nsfw_role.name} has been added to you.',
                                              icon=message.author.avatar_url,
                                              colour=nsfw_role.colour)
                await message.channel.send(embed=response)

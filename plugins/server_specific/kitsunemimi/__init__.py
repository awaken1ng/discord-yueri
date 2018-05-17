import utils
from core.plugin import BasePlugin


class ServerPlugin(BasePlugin):
    servers = (222552805393694720,)

    @staticmethod
    async def log_in_channel(log_channel, **kwargs):
        log_msg = utils.create_embed(**kwargs)
        await log_channel.send(embed=log_msg)

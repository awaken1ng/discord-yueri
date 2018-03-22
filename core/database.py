import motorengine
from motorengine.document import Document
from motorengine.fields import IntField, ListField


class GuildSettings(Document):
    guild_id = IntField(required=True)
    toggleable_roles = ListField(IntField())  # List of toggleable role IDs
    underage = ListField(IntField())  # List of IDs of underage users


class Database:
    def __init__(self, bot):
        self.bot = bot
        self._logger = bot.log.get_logger('Database')

        config = bot.config['Database']
        self.client = motorengine.connect(db=config['name'], host=config['connection_string'])
        self.bot.loop.create_task(self._startup_check())

    async def _startup_check(self):
        server_info = await self.client.connection.server_info()
        self._logger.info(f"Connected to MongoDB v{server_info['version']}")

    async def get_guild_settings(self, guild_id: int):
        settings = await GuildSettings.objects.get(guild_id=guild_id)
        if not settings:
            settings = GuildSettings(guild_id=guild_id)
            settings.save()
        return settings

    async def get_guild_setting(self, guild_id: int, setting: str):
        settings = await self.get_guild_settings(guild_id)
        return getattr(settings, setting)

    async def set_guild_setting(self, guild_id: int, setting: str, value):
        settings = await self.get_guild_settings(guild_id)
        setattr(settings, setting, value)
        settings.save()

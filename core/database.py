from motor.motor_asyncio import AsyncIOMotorClient
from umongo import MotorAsyncIOInstance, Document
from umongo.fields import IntegerField, ListField, DictField
from pymongo.errors import ServerSelectionTimeoutError


instance = MotorAsyncIOInstance()


@instance.register
class GuildSettings(Document):
    guild_id = IntegerField(required=True)
    toggleable_roles = ListField(IntegerField())  # List of toggleable role IDs
    underage = ListField(IntegerField())   # List of IDs of underage users
    counters = DictField()


class Database:
    def __init__(self, bot):
        self.bot = bot
        self._logger = bot.log.get_logger('Database')

        config = bot.config['Database']
        self.client = AsyncIOMotorClient(config['connection_string'])
        self.db = self.client[config['name']]
        instance.init(self.db)
        self.bot.loop.create_task(self._startup_check())

    async def _startup_check(self):
        try:
            server_info = await self.client.server_info()
            self._logger.info(f"Connected to MongoDB v{server_info['version']}")
        except ServerSelectionTimeoutError as error:
            self._logger.critical('Could not establish connection to MongoDB')
            raise error

    async def get_guild_settings(self, guild_id: int):
        settings = await GuildSettings.find_one({'guild_id': guild_id})
        if not settings:
            settings = GuildSettings(guild_id=guild_id)
            await settings.commit()
        return settings

    async def get_guild_setting(self, guild_id: int, setting: str):
        settings = await self.get_guild_settings(guild_id)
        return getattr(settings, setting)

    async def set_guild_setting(self, guild_id: int, setting: str, value):
        settings = await self.get_guild_settings(guild_id)
        setattr(settings, setting, value)
        await settings.commit()

import aioinflux
import aiohttp


class Influx:
    def __init__(self, bot):
        self.bot = bot
        self._logger = bot.log.get_logger('Influx')

        self.config = bot.config['Monitoring']
        self.client = aioinflux.InfluxDBClient(**self.config['influx']) \
            if self.config['enabled'] \
            else None

        bot.loop.create_task(self._startup_check())

    async def _startup_check(self):
        if not self.client:
            return
        ping = await self.client.ping()
        self._logger.info(f"Connected to InfluxDB v{ping['X-Influxdb-Version']}")

        # Check if database is present
        dbs = await self.client.show_databases()
        db_name = self.config['influx']['db']
        if [db_name] not in dbs['results'][0]['series'][0]['values']:
            self._logger.info('No database present, creating')
            await self.client.query(f'CREATE DATABASE "{db_name}" WITH DURATION 2w REPLICATION 1')

    async def write(self, data: dict):
        if not self.client or not self.bot.user:
            # Monitoring is disabled or client didn't initialize yet
            self._logger.debug(f'Disabled or client is not ready: {data}')
            return

        # Add `client_id` tag
        # Cast the ID into string, because apparently tags expect strings
        if 'tags' not in data.keys():
            data['tags'] = {'client_id': str(self.bot.user.id)}
        else:
            if 'client_id' not in data['tags'].keys():
                data['tags']['client_id'] = str(self.bot.user.id)

        try:
            await self.client.write(data)
            self._logger.debug(f'Report sent: {data}')
        except aiohttp.client_exceptions.ClientConnectionError as error:
            self._logger.error(f'Failed to report: {data}, due to {error}')

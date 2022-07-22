import uuid

import aiounittest

from yessql import AioMySQL, MySQLConfig


class MySQLTestConfig(MySQLConfig):
    db = 'yessql'

    class Config:
        env_prefix = 'MYSQL_'


class TestAioMySQL(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        self.config = MySQLTestConfig()
        self.mysql = AioMySQL(self.config)

    async def setup_pool(self):
        await self.mysql.setup_pool()
        assert self.mysql.pool._closed is False
        await self.mysql.close_pool()
        assert self.mysql.pool._closed is True

    async def test_read(self):
        await self.mysql.setup_pool()
        async for row in self.mysql.read('SELECT * FROM guitars'):
            assert row is not None
        await self.mysql.close_pool()

    async def test_read_with_params(self):
        _id = 'b7337fa5-3e17-4628-b4db-00af02e07fdc'
        await self.mysql.setup_pool()
        async for row in self.mysql.read(
            query='SELECT * FROM guitars WHERE id = %s', params=(_id,)
        ):
            assert row['id'] == _id
        await self.mysql.close_pool()

    async def test_read_all(self):
        await self.mysql.setup_pool()
        data = await self.mysql.read_all('SELECT * FROM guitars')
        assert len(data) == 1
        await self.mysql.close_pool()

    async def write(self):
        _id = str(uuid.uuid4())
        await self.mysql.setup_pool()
        await self.mysql.write(stmt='INSERT INTO guitars (id) VALUES (%s)', params=(_id,))
        result = await self.mysql.read_all('SELECT * FROM guitars WHERE id = %s', (_id,))
        assert result[0]['id'] == _id
        await self.mysql.close_pool()

    async def test_commit(self):
        await self.mysql.setup_pool()
        await self.mysql.commit('CREATE TABLE from_test (id text)')
        tables = await self.mysql.read_all("show tables like 'from_test';")
        assert len(tables) == 1
        await self.mysql.commit('DROP TABLE from_test')
        await self.mysql.close_pool()

    async def test_context_manager(self):
        async with self.mysql as mysql:
            assert mysql.pool._closed is False
            data = await mysql.read_all('SHOW TABLES')
            assert data is not None
        assert mysql.pool._closed is True

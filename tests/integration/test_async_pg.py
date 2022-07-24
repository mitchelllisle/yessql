from asyncio import TimeoutError

import aiounittest
import pytest
from asyncpg import Record
from pydantic import UUID4, BaseModel

from yessql import AioPostgres, PostgresConfig


class PGTestConfig(PostgresConfig):
    database = 'yessql'

    class Config:
        env_prefix = 'PG_'


class TestAioPostgres(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        self.config = PGTestConfig()
        self.postgres = AioPostgres(self.config)

    async def setup_pool(self):
        await self.postgres.setup_pool()
        assert self.postgres.pool._closed is False
        await self.postgres.close_pool()
        assert self.postgres.pool._closed is True

    async def test_read(self):
        await self.postgres.setup_pool()
        async for row in self.postgres.read('SELECT * FROM instruments.guitars'):
            assert isinstance(row, Record)
        await self.postgres.close_pool()

    async def test_read_with_params(self):
        _id = 'b7337fa5-3e17-4628-b4db-00af02e07fdc'
        _type = 'semi-hollow-electric'
        await self.postgres.setup_pool()
        async for row in self.postgres.read(
            query='SELECT * FROM instruments.guitars WHERE id = {id} AND type = {type}',
            params={'id': _id, 'type': _type},
        ):
            assert str(row['id']) == _id
            assert str(row['type']) == _type
        await self.postgres.close_pool()

    async def test_read_all(self):
        await self.postgres.setup_pool()
        data = await self.postgres.read_all('SELECT * FROM instruments.guitars')
        assert len(data) == 3
        await self.postgres.close_pool()

    async def test_commit(self):
        await self.postgres.setup_pool()
        await self.postgres.commit('CREATE TABLE from_test (id text)')
        tables = await self.postgres.read_all(
            "select * from pg_tables where tablename = 'from_test';"
        )
        assert len(tables) == 1
        await self.postgres.commit('DROP TABLE from_test')
        await self.postgres.close_pool()

    async def test_context_manager(self):
        async with self.postgres as pg:
            assert pg.pool._closed is False
            data = await pg.read_all('select * from pg_tables')
            assert data is not None
        assert pg.pool._closed is True

    async def test_query_low_timeout(self):
        with pytest.raises(TimeoutError):
            async with AioPostgres(self.config, timeout=1) as pg:
                await pg.read_all('SELECT pg_sleep(3)')

    async def test_query_with_model(self):
        class Guitars(BaseModel):
            id: UUID4
            make: str
            model: str
            type: str

        async with AioPostgres(self.config) as pg:
            data = await pg.read_all('SELECT * from instruments.guitars', model=Guitars)

        row = data[0]
        assert all(map(lambda x: isinstance(x, Guitars), data))
        assert str(row.id) == 'b7337fa5-3e17-4628-b4db-00af02e07fdc'
        assert row.make == 'rickenbacker'
        assert row.model == '330'
        assert row.type == 'semi-hollow-electric'

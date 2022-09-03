import uuid
from asyncio import TimeoutError
from random import SystemRandom

import aiounittest
import pytest
from asyncpg import Record
from pydantic import UUID4, BaseModel

from yessql import AioPostgres, PostgresConfig


class PGTestConfig(PostgresConfig):
    database = 'yessql'

    class Config:
        env_prefix = 'PG_'


class Guitars(BaseModel):
    id: UUID4
    make: str
    model: str
    type: str
    source: str


def make_guitar_row(source: str) -> Guitars:
    guitars = {
        'Fender': ['Stratocaster', 'Jazzmaster', 'Mustang'],
        'Gibson': ['SG', 'Les Paul'],
        'Rickenbacker': ['330', '330/12'],
    }
    make = SystemRandom().choice(list(guitars.keys()))
    model = SystemRandom().choice(guitars[make])
    return Guitars(id=str(uuid.uuid4()), make=make, model=model, type='electric', source=source)


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
            query='SELECT * FROM instruments.guitars WHERE id = ${id} AND type = ${type}',
            params={'id': _id, 'type': _type},
        ):
            assert str(row['id']) == _id
            assert str(row['type']) == _type
        await self.postgres.close_pool()

    async def test_read_all(self):
        await self.postgres.setup_pool()
        data = await self.postgres.read_all(
            "SELECT * FROM instruments.guitars WHERE source = 'init'"
        )
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
        source = 'test-query-with-model'
        guitar = make_guitar_row(source)
        async with AioPostgres(self.config) as pg:
            await pg.write(
                """INSERT INTO instruments.guitars 
                VALUES (${id}, ${make}, ${model}, ${type}, ${source})""",
                [guitar.dict()],
            )
            data = await pg.read_all(
                'SELECT * from instruments.guitars where id = ${id}',
                {'id': str(guitar.id)},
                model=Guitars,
            )

        row = data[0]
        assert all(map(lambda x: isinstance(x, Guitars), data))
        assert row.id == guitar.id
        assert row.make == guitar.make
        assert row.model == guitar.model
        assert row.type == guitar.type

    async def test_write(self):
        rows = [make_guitar_row('test-write').dict() for _ in range(100)]
        stmt = """
            INSERT INTO instruments.guitars VALUES (${id}, ${make}, ${model}, ${type}, ${source})
        """
        async with AioPostgres(self.config) as pg:
            await pg.write(stmt, rows)
            output = await pg.read_all(
                'SELECT * FROM instruments.guitars WHERE source = ${source}',
                params={'source': 'test-write'},
                model=dict,
            )
            await pg.commit("DELETE FROM instruments.guitars WHERE source = 'test-write'")
        assert output == rows

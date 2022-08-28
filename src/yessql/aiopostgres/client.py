from abc import ABC
from typing import AsyncGenerator, Dict, Tuple, Type, Union

from asyncpg import Pool, create_pool
from pydantic import BaseModel

from yessql.aiopostgres.params import NamedParams
from yessql.clients import AsyncDatabaseClient
from yessql.config import PostgresConfig
from yessql.utils import PendingConnection


class AioPostgres(AsyncDatabaseClient, ABC):
    def __init__(
        self, config: PostgresConfig, timeout: int = None, min_size: int = 1, max_size: int = 10
    ):
        """
        AioPostgres is an async postgres client that allows you to set up a connection pool for
        Postgres and read and write data asynchronously. Contains an async context manager for easy
        setup and closing of the connections that you open.
        Args:
            config: a DatabaseConfig object that contains all the connection details for postgres
            timeout: max time before a query is cancelled
            min_size: The minimum # of connections that will be reserved for this client
            max_size: The maximum # of connections that will be reserved for this client
        """
        self.pool: Union[PendingConnection, Pool] = PendingConnection()
        self.config: PostgresConfig = config
        self.timeout = timeout
        super().__init__(config, min_size, max_size)

    @property
    def closed(self) -> bool:
        return self.pool._closed  # noqa

    async def setup_pool(self) -> None:
        self.pool = await create_pool(
            host=self.config.host.get_secret_value(),
            port=self.config.port,
            user=self.config.user.get_secret_value(),
            password=self.config.password.get_secret_value(),
            database=self.config.database,
            command_timeout=self.timeout,
            min_size=self.min_size,
            max_size=self.max_size,
        )

    async def close_pool(self) -> None:
        """Close Connection Pool

        Close the connection pool. If you're running this class inside a context manager (which you
        should be) then this will get called as part of exiting the context.

        Returns:
            None

        """
        await self.pool.close()  # type: ignore

    async def read(
        self, query: str, params: Dict = None, model: Type[BaseModel] = None
    ) -> AsyncGenerator:
        _params = NamedParams(**params) if params is not None else None
        _query = query.format_map(_params)

        async with self.pool.acquire() as conn:  # type: ignore
            async with conn.transaction():
                cur = conn.cursor(_query, *_params.as_tuple) if _params else conn.cursor(_query)
                async for row in cur:
                    if model:
                        yield model(**row)
                    else:
                        yield row

    async def write(self, stmt: str, params: Tuple) -> None:
        """
        Write data to a table with the given statement and data
        Args:
            stmt: The Insert statement you want to run
            params: The data to pass as params

        Returns:
            None
        """
        _params = NamedParams(**params) if params is not None else None
        _query = query.format_map(_params)
        async with self.pool.acquire() as conn:  # type: ignore
            async with conn.transaction():
                await conn.executemany(_query, _params)

    async def commit(self, stmt: str) -> None:
        """
        Run a command against the database. This is useful for statements where you need to change
        the database in some way E.g. ALTER, CREATE, DROP statements etc.
        Args:
            stmt: The statement to run
        """
        async with self.pool.acquire() as conn:  # type: ignore
            await conn.execute(stmt)

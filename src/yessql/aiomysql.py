from abc import ABC
from typing import AsyncGenerator, Tuple, Type, Union

import aiomysql as mysql
from pydantic import BaseModel

from yessql.clients import AsyncDatabaseClient
from yessql.config import MySQLConfig
from yessql.utils import PendingConnection


class AioMySQL(AsyncDatabaseClient, ABC):
    def __init__(
        self,
        config: MySQLConfig,
        cursor_class: mysql.Cursor = mysql.SSDictCursor,
        min_size: int = 1,
        max_size: int = 10,
    ):
        self.pool: Union[mysql.Pool, PendingConnection] = PendingConnection()
        self.config: MySQLConfig = config
        self.cursor_class: mysql.Cursor = cursor_class
        super().__init__(config, min_size, max_size)

    async def setup_pool(self):
        """Setup Connection Pool

        We use connection pools for connecting to MySQL. This method can be used to set up the
        connection - however you will need to call `close_pool` to ensure all database connections
        are correctly closed when no longer needed. Although some situations may require you to do
        these steps manually, you should (where possible) use the context manager aspect of this
        class (I.E. using a with statement) since this will handle closing the connection for you.

        Returns:
            Nothing is returned. This will instead initialise the pool property.

        """
        self.pool = await mysql.create_pool(
            host=self.config.host.get_secret_value(),
            user=self.config.user.get_secret_value(),
            password=self.config.password.get_secret_value(),
            db=self.config.database,
            port=self.config.port,
            minsize=self.min_size,
            maxsize=self.max_size,
        )

    async def read(
        self, query: str, params: Tuple = None, model: Type[BaseModel] = None
    ) -> AsyncGenerator:
        """
        Read results from postgres and return an AsyncGenerator. This allows you to read large
        amounts of data without having to store them in memory.
        Args:
            query: The query you want to return data for
            params: Any params you need to pass to the query
            model: An optional pydantic.BaseModel we'll use as the row return type

        Returns:
            An AsyncGenerator
        """
        async with self.pool.acquire() as conn:  # type: ignore
            async with conn.cursor(self.cursor_class) as cur:
                await cur.execute(query, params)
                async for row in cur:
                    if model:
                        yield model(**row)
                    else:
                        yield row

    async def write(self, stmt: str, params: Union[Tuple, str, int]) -> None:
        """
        Write data to a table with the given statement and data
        Args:
            stmt: The Insert statement you want to run
            params: The data to pass as params

        Returns:
            None
        """
        async with self.pool.acquire() as conn:  # type: ignore
            async with conn.cursor() as cur:
                await cur.executemany(stmt, params)
            await conn.commit()

    async def commit(self, stmt: str):
        """
        Run a command against the database. This is useful for statements where you need to change
        the database in some way E.g. ALTER, CREATE, DROP statements etc.
        Args:
            stmt: The statement to run
        """
        async with self.pool.acquire() as conn:  # type: ignore
            async with conn.cursor() as cur:
                await cur.execute(stmt)
            await conn.commit()

    async def close_pool(self) -> None:
        """Close Connection Pool

        Close the connection pool. If you're running this class inside a context manager (which you
        should be) then this will get called as part of exiting the context.

        Returns:
            None

        """
        self.pool.close()
        await self.pool.wait_closed()

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, NewType, Tuple, Type, Union

from pydantic import BaseModel

from yessql.config import DatabaseConfig
from yessql.utils import PendingConnection

DatabasePool = NewType('DatabasePool', object)


class AsyncDatabaseClient(ABC):
    def __init__(self, config: DatabaseConfig, min_size: int, max_size: int):
        self.pool: Union[PendingConnection, DatabasePool] = PendingConnection()
        self.config = config
        self.min_size = min_size
        self.max_size = max_size

    @abstractmethod
    async def setup_pool(self) -> None:
        pass

    @abstractmethod
    async def close_pool(self) -> None:
        pass

    @abstractmethod
    async def read(
        self, query: str, params: Dict = None, model: Type[BaseModel] = None
    ) -> AsyncGenerator:
        """
        Read results from postgres and return an AsyncGenerator. This allows you to read large
        amounts of data without having to store them in memory.
        Args:
            query: The query you want to return data for
            params: Any params you need to pass to the query
            model: An optional pydantic.BaseModel that each row will be parsed to

        Returns:
            An AsyncGenerator
        """
        pass

    async def read_all(
        self, query: str, params: Dict = None, model: Type[BaseModel] = None
    ) -> Union[List[Dict], Type[BaseModel]]:
        """
        In some cases you might want to just return the data without dealing with iteration you can
        use this. We'll return all the records in a list. Be careful using this for large datasets
        as it will try and load everything in memory.
        Args:
            query: The query you want to return data for
            params: Any params you need to pass to the query
            model: An optional pydantic.BaseModel we'll use as the row return type

        Returns:
            A List of Records
        """
        rows = []
        async for row in self.read(query=query, params=params, model=model):  # type: ignore
            rows.append(row)
        return rows

    @abstractmethod
    async def write(self, stmt: str, params: Tuple) -> None:
        """
        Write data to a table with the given statement and data
        Args:
            stmt: The Insert statement you want to run
            params: The data to pass as params

        Returns:
            None
        """
        pass

    @abstractmethod
    async def commit(self, stmt: str) -> None:
        """
        Run a command against the database. This is useful for statements where you need to change
        the database in some way E.g. ALTER, CREATE, DROP statements etc.
        Args:
            stmt: The statement to run
        """
        pass

    def writer(self, stmt: str):
        """return a writer for the given statement.

        Basically just curry's the write method into a coroutine that accepts a batch of parameters
        and writes using the given statement. Obviously this is useful if you are batching inserts.

        Args:
            stmt: The Insert statement you want to run
        """

        async def writer(batch):
            await self.write(stmt, batch)

        return writer

    async def __aenter__(self):
        await self.setup_pool()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_pool()

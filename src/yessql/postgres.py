from typing import Dict, Generator, List, Tuple, Union

import pg8000.dbapi as postgresql

from yessql.config import PostgresConfig
from yessql.utils import PendingConnection, PendingConnectionError


class ContextCursor(postgresql.Cursor):
    """**ContextCursor**

    For some reason cursors always require you to define an explicit connect and close. This turns
    these operations into a context manager to make it safer and ensure the cursor is closed after
    use.
    """

    def __enter__(self):
        if isinstance(self.connection, PendingConnection):
            raise PendingConnectionError(
                'Connection to database has not been made. '
                'Did you forget to call the setup_connection() method?'
            )
        else:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Postgres:
    """**Blocking Postgres Client**

    Synchronous Postgres client for interacting with Postgres databases. For Asynchronous
    Postgres client see yessql.AioPostgres
    """

    def __init__(self, config: PostgresConfig):
        """
        Args:
            config: A PostgresConfig object for connecting to the database
        """
        self.config = config
        self.connection: Union[postgresql.Connection, PendingConnection] = PendingConnection()

    def setup_connection(self) -> None:
        """
        Make a call to the database and attempt to set up a connection. This can either be called
        explicitly or will be called as part of a context statement (I.e. using `with`)

        Returns:
            None
        """
        self.connection = postgresql.connect(
            host=self.config.host.get_secret_value(),
            port=self.config.port,
            user=self.config.user.get_secret_value(),
            password=self.config.password.get_secret_value(),
            database=self.config.database,
        )

    def close_connection(self) -> None:
        """
        Close the connection to the database. Can be used explicitly or will be called as you exit
        out of a context managed statement.

        Returns:
            None
        """
        self.connection.close()

    def __enter__(self):
        self.setup_connection()
        return self

    def __exit__(self, *args):
        self.close_connection()

    def write(self, stmt: str, rows: List[Tuple]) -> int:
        """
        Write some data to the database by passing an insert statement and a list of tuples for the
        rows
        Args:
            stmt: The insert statement to run. `%s` placeholders are used for indicating params
            rows: A list of tuples containing the data to pass to the above query.

        Returns:
            Row count as an integer

        """
        with ContextCursor(connection=self.connection) as cursor:
            cursor.executemany(stmt, rows)
            self.connection.commit()
            return cursor.rowcount

    def commit(self, stmt: str) -> int:
        """
        Although mostly the same as the write method - commit is useful for identifying when you
        are making changes to the database and not pass params. Use this for any CREATE, DROP etc.
        statements where you are managing the database to indicate to other developers where you are
        changing the database VS writing data to it
        Args:
            stmt: The statement to run

        Returns:
            Row count

        """
        with ContextCursor(connection=self.connection) as cursor:
            cursor.execute(stmt)
            self.connection.commit()
            return cursor.rowcount

    def read(self, query: str, params: Tuple = None) -> Generator:
        """
        Read data from the database using the given query and params. This is a generator meaning
        you can iterate through the rows without loading them all into memory.
        Args:
            query: The query to run
            params: Any params to be substituted for `%s` strings in above query

        Returns:
            A generator

        """
        with ContextCursor(self.connection) as cursor:
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            keys = [k[0] for k in cursor.description]
            for row in cursor:
                yield dict(zip(keys, row))

    def read_all(self, query: str, params: Tuple = None) -> List[Dict]:
        """
        If you want to return all rows from the query without worrying about memory management
        then this method is useful. It will return a list of dictionaries containing the results
        of the query
        Args:
            query: The query to run
            params: Any params to be substituted for `%s` strings in above query

        Returns:
            A list of dicts with the data from the query

        """
        return [row for row in self.read(query, params)]

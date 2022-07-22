import unittest
import uuid

import pytest
from pg8000.dbapi import Connection
from pg8000.exceptions import DatabaseError

from yessql import (
    ContextCursor,
    PendingConnection,
    PendingConnectionError,
    Postgres,
    PostgresConfig,
)


class PGTestConfig(PostgresConfig):
    database = 'siphon'

    class Config:
        env_prefix = 'PG_'


class TestPg(unittest.TestCase):
    def setUp(self) -> None:
        self.config = PGTestConfig()
        self.pg = Postgres(self.config)
        self.pg.setup_connection()

    def test_read_postgres(self):
        row = next(self.pg.read('select * from instruments.guitars'))
        assert str(row['id']) == 'b7337fa5-3e17-4628-b4db-00af02e07fdc'

    def test_write_to_postgres(self):
        _id = str(uuid.uuid4())
        self.pg.write(
            stmt='INSERT INTO instruments.guitars (id, make, model, type) VALUES (%s, %s, %s, %s)',
            rows=[(_id, 'test', 'test', 'test')],
        )
        # clean up test data afterwards
        self.pg.write('DELETE FROM instruments.guitars WHERE id = $1', [(_id,)])

    def test_commit(self):
        self.pg.commit('CREATE TABLE test (id text)')
        self.pg.read_all('SELECT * FROM test')
        self.pg.commit('DROP TABLE test')
        with pytest.raises(DatabaseError) as err:
            self.pg.read_all('SELECT * FROM test')
        assert 'relation "test" does not exist' in str(err.value)

    def test_pending_connection(self):
        conn = PendingConnection()
        with pytest.raises(PendingConnectionError):
            with conn:
                pass

    def test_pending_connection_with_normal_connect(self):
        conn = Postgres(self.config)
        assert isinstance(conn.connection, PendingConnection)
        with pytest.raises(PendingConnectionError):
            conn.read_all('SELECT 1')

    def test_connection_with_normal_connect(self):
        conn = Postgres(self.config)
        assert isinstance(conn.connection, PendingConnection)
        conn.setup_connection()
        assert isinstance(conn.connection, Connection)

    def test_context_cursor_pending(self):
        conn = Postgres(self.config)
        with pytest.raises(PendingConnectionError):
            with ContextCursor(conn.connection):
                pass

    def test_context_cursor_connection(self):
        with ContextCursor(self.pg.connection) as cur:
            cur.execute('SELECT 1')
            assert next(cur) == [1]
        # this means cursor has been closed
        assert cur.connection is None

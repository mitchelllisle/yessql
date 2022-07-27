import pytest

from yessql.clients import AsyncDatabaseClient


def test_abstract_method_fails(database_config):
    class BadDB(AsyncDatabaseClient):
        pass

    with pytest.raises(TypeError):
        BadDB(database_config, min_size=1, max_size=1)

import pytest

from yessql.config import DatabaseConfig, MySQLConfig, PostgresConfig


@pytest.fixture()
def mysql_config() -> MySQLConfig:
    return MySQLConfig()


@pytest.fixture()
def postgres_config() -> PostgresConfig:
    return PostgresConfig()


@pytest.fixture()
def database_config() -> DatabaseConfig:
    return DatabaseConfig()

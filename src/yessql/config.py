from typing import Optional

from pydantic import BaseSettings, Extra, SecretStr


class DatabaseConfig(BaseSettings):
    """Config object for connecting to databases.

    This is a generic config object that can be subclassed to create database specific config and
    extended to include specific functionality or defaults relevant to that database technology.

    Notes:
        You probably want to import and use database specific configs such as MySQLConfig and
        PostgresConfig. This is simply a parent class with common config.

    Attributes:
        host: The host name to connect to
        port: The port to use for connections
        user: The username to authenticate with
        password: The password to authenticate with

    """

    host: SecretStr
    port: int
    user: SecretStr
    password: SecretStr

    class Config:
        extra = Extra.ignore


class MySQLConfig(DatabaseConfig):
    """

    Attributes:
        host: The host name to connect to
        port: The port to use for connections
        user: The username to authenticate with
        password: The password to authenticate with
        db: Optional attribute for the database to connect to
    """

    port: int = 3306
    database: Optional[str]


class PostgresConfig(DatabaseConfig):
    port: int = 5432
    database: str

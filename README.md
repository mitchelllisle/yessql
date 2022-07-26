##  YesSQL

[![build-test-docs-publish](https://github.com/mitchelllisle/yessql/actions/workflows/run-build-tests-docs-publish.yaml/badge.svg?branch=main)](https://github.com/mitchelllisle/yessql/actions/workflows/run-build-tests-docs-publish.yaml)
[![CodeQL](https://github.com/mitchelllisle/yessql/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/mitchelllisle/yessql/actions/workflows/codeql-analysis.yml)

# Welcome to YesSQL

> ⚠️ Caution: This library is still in active development and is subject to change until we reach a stable 
> version. Please report any bugs/issues/ideas or features to our [GitHub repo](https://github.com/mitchelllisle/yessql)

## What is YesSQL?
YesSQL is a Python database library that simplifies the way you connect to and interact with common
SQL databases.


## Usage
For more comprehensive documentation see out [docs](https://mitchelllisle.github.io/yessql/).

**Install from PyPi**
```shell
pip install yessql
```

**Reading data**

```python
import asyncio
from yessql import AioPostgres, PostgresConfig

async def main():
    config = PostgresConfig(
        host="localhost",
        username="my_username",
        password="my_password",
        database="my_database"
    )
    
    async with AioPostgres(config) as pg:
        async for row in pg.read("SELECT * FROM table"):
            print(row)


if __name__ == '__main__':
    asyncio.run(main())

```

**Writing Data**

```python
import asyncio
from yessql import AioPostgres, PostgresConfig

async def main():
    config = PostgresConfig(
        host="localhost",
        username="my_username",
        password="my_password",
        database="my_database"
    )
    
    async with AioPostgres(config) as pg:
        await pg.write(
            stmt="INSERT INTO table (id, name) VALUES ($1, $2)",
            params=[("1", "john"), ("2", "paul")]
        )


if __name__ == '__main__':
    asyncio.run(main())
```


1. You can easily swap out the Postgres variants for MySQL or omit Aio for non-async variants


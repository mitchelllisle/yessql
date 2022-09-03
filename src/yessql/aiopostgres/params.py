from typing import Iterable, List, Tuple

from pipe import map


class NamedParams(dict):
    @property
    def as_tuple(self) -> Tuple:
        return tuple(self.values())

    def __getitem__(self, key):
        return f'{list(self.keys()).index(key) + 1}'


class NamedParamsList:
    def __init__(self, items: Iterable):
        self.items = list(
            items
            | map(lambda item: dict(sorted(item.items())))
            | map(lambda item: NamedParams(**item))
        )

    def format_map(self, stmt: str) -> str:
        return stmt.format_map(self.items[0])

    def as_tuples(self) -> List[Tuple]:
        return list(self.items | map(lambda item: item.as_tuple))

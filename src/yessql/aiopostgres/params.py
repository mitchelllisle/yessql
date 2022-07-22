from typing import Tuple


class NamedParams(dict):
    @property
    def as_tuple(self) -> Tuple:
        return tuple(self.values())

    def __getitem__(self, key):
        return f'${list(self.keys()).index(key) + 1}'

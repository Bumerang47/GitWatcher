from dataclasses import dataclass

from urllib.parse import urlparse


@dataclass
class Contributor:
    name: str
    count: int
    email: str = ''

    @staticmethod
    def columns():
        return ('email', 'count')

    def __eq__(self, other):
        if isinstance(other, str):
            return self.email == other
        return super().__eq__(other)


@dataclass
class Destination:
    owner: str
    repo: str

    @classmethod
    def from_str(cls, v):
        u = urlparse(v)
        args = u.path.strip('/').split('/')
        if len(args) != 2:
            raise ValueError('Incorect repository url')
        return cls(*args)

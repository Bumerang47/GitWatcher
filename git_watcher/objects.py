from dataclasses import dataclass

from urllib.parse import urlparse


@dataclass(unsafe_hash=True)
class Contributor:
    login: str
    count: int = 0
    email: str = ''

    @staticmethod
    def columns():
        return ('login', 'count')

    def __eq__(self, other):
        if isinstance(other, str):
            return self.login == other
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

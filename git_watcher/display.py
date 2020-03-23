import os
from dataclasses import asdict, is_dataclass
from itertools import cycle
from typing import List, Dict

from . import logger

__all__ = ('clear_output', 'Throbber', 'Table')


def clear_output():
    for h in logger.handlers:
        h.close()

    term = os.getenv('TERM')
    if not term:
        return
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


class Throbber:
    symbols = ('⠇', '⠏', '⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧')
    iter = iter(cycle(symbols))

    def __repr__(self):
        return next(self.iter)


class Table:
    columns: Dict[str, int]  # Dict[head, column size]
    rows: List[str]
    margin = 4

    def __init__(self, cls, data, weight=5):
        self.columns = {key: max(weight, len(key)) for key in cls.columns()}
        self.rows = []
        for i, item in enumerate(data, start=1):
            if is_dataclass(item):
                item = asdict(item)
            item['id'] = str(i)

            row: List[str] = []
            for head, w in self.columns.items():
                v = str(item.get(head, ''))
                self.columns[head] = max(w, len(v))
                row.append(v)
            self.rows.append(row)

    def __str__(self):
        sizes = []
        header = []
        for c, w in self.columns.items():
            size = w + self.margin
            sizes.append(size)
            header.append(c.upper().ljust(size))

        resp = [''.join(header)]
        for row in self.rows:
            resp.append(''.join(
                cell.ljust(sizes[i]) for i, cell in enumerate(row)
            ))
        return '\n'.join(resp)

from typing import List
from allstars.core.join import Join


class QueryContext:
    key: str
    joins: List[Join] = []

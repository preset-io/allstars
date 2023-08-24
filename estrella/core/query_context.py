from typing import List
from estrella.core.join import Join

class QueryContext:
    key: str
    joins: List[Join] = []

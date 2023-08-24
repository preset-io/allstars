from dataclasses import dataclass
from typing import Literal, List

from estrella.core.base import Serializable


@dataclass
class Column(Serializable):
    name: str
    data_type: str


@dataclass
class Relation(Serializable):
    # the database schema
    database_schema: str
    # the view_name or table_name
    reference: str
    relation_type: Literal["view", "table"]
    columns: List[Column]

    @property
    def key(self):
        return f"{self.database_schema}.{self.reference}"

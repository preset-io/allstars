from dataclasses import dataclass
from typing import Literal, List

from estrella.core.base import Serializable
from estrella.core.join import Join


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

    def find_common_columns(self, relation):
        matches = []
        col_name_set = {c.name for c in relation.columns}
        for c in self.columns:
            if c.name in col_name_set:
                matches.append(c)
        return matches

    def gen_join(self, relation, columns: list):
        col_names = [c.name for c in columns]
        criteria = " AND ".join(
            [f"{self.key}.{c} = {relation.key}.{c}" for c in col_names]
        )
        return Join(
            left_relation_key=self.key,
            right_relation_key=relation.key,
            join_criteria=criteria,
            cardinality="unknown",
            join_term="LEFT JOIN",
        )

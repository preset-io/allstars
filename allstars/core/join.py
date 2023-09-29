from typing import Literal
from dataclasses import dataclass

from allstars.core.base import Serializable


@dataclass
class Join(Serializable):
    left_relation_key: str
    right_relation_key: str
    join_criteria: str
    cardinality: Literal["many_to_one", "one_to_many", "many_to_many"]
    join_term: Literal["JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]

    @property
    def key(self):
        return f"{self.left_relation_key}.{self.right_relation_key}"

    def to_sql(self):
        return f"{self.join_term} ON {self.join_criteria}"

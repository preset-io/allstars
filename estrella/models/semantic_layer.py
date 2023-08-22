from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, Json


class _Object(BaseModel):
    """Any object living in the SemanticLayer's menu"""

    key: str
    label: Optional[str] = None
    description: Optional[str] = None


class Relation(BaseModel):
    """A pointer to a physical table or a view"""

    # the database schema
    schema: str
    # the view_name or table_name
    reference: str

    relation_type: Literal["view", "table"]


class _SelectExpression(_Object):
    """Private class for something that lives in a SELECT"""

    expression: str

    # Usually a single relation is involved, but sometimes two
    # as in SUM(DATE_DIFF(A.dt, B.dt))
    relation_keys: List[str]


class Metric(_SqlExpression):
    """Just a good old metric"""

    pass


class Dimension(_SelectExpression):
    """A simple dimension"""

    pass


class Filter(_SelectExpression):
    """
    A predefined filter that can be added to a WHERE clause
    """

    pass


class Join(SqlObject):
    left_relation_key: str
    right_relation_key: str
    join_criteria: str
    cardinality: Literal["many_to_one", "one_to_many", "many_to_many"]
    join_term: Literal["JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]


class Folder(_Object):
    parent_folder_key: Optional[str] = None


class QueryContext(BaseModel):
    key: str
    joins: List[Join] = []


class SemanticLayer(BaseModel):
    metrics: List[Metric] = []
    dimension: List[Dimension] = []
    joins: List[Join] = []
    query_contexts: List[QueryContext] = []
    folders: List[Filters] = []
    filters: List[Filters] = []

    relations: List[Relation] = []
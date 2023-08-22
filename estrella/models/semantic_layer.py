from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, Json


class _Object(BaseModel):
    """Any object living in the SemanticLayer's menu"""

    key: str
    label: Optional[str] = None
    description: Optional[str] = None


class ColumnModel(BaseModel):
    name: str
    data_type: str


class RelationModel(BaseModel):
    """A pointer to a physical table or a view"""

    # the database schema
    database_schema: str
    # the view_name or table_name
    reference: str
    columns: List[ColumnModel]

    relation_type: Literal["view", "table"]


class _SelectExpressionModel(_Object):
    """Private class for something that lives in a SELECT"""

    expression: str

    # Usually a single relation is involved, but sometimes two
    # as in SUM(DATE_DIFF(A.dt, B.dt))
    relation_keys: List[str]


class MetricModel(_SelectExpressionModel):
    """Just a good old metric"""

    pass


class DimensionModel(_SelectExpressionModel):
    """A simple dimension"""

    pass


class FilterModel(_SelectExpressionModel):
    """
    A predefined filter that can be added to a WHERE clause
    """

    pass


class JoinModel(_Object):
    left_relation_key: str
    right_relation_key: str
    join_criteria: str
    cardinality: Literal["many_to_one", "one_to_many", "many_to_many"]
    join_term: Literal["JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]


class FolderModel(_Object):
    parent_folder_key: Optional[str] = None


class QueryContextModel(BaseModel):
    key: str
    joins: List[JoinModel] = []


class SemanticLayerModel(BaseModel):
    metrics: List[MetricModel] = []
    dimension: List[DimensionModel] = []
    joins: List[JoinModel] = []
    query_contexts: List[QueryContextModel] = []
    folders: List[FolderModel] = []
    filters: List[FilterModel] = []

    relations: List[RelationModel] = []

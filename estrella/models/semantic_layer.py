from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, Json
import yaml


class CustomModel(BaseModel):

    def to_yaml(self) -> str:
        return yaml.dump(self.dict())

    def to_yaml_file(self, filename: str) -> None:
        with open(filename, 'w') as file:
            yaml.dump(self.dict(), file, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_string: str):
        data = yaml.load(yaml_string, Loader=yaml.FullLoader)
        return cls(**data)

    @classmethod
    def from_yaml_file(cls, filename: str):
        with open(filename, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return cls(**data)


class _Object(CustomModel):
    """Any object living in the SemanticLayer's menu"""

    key: str
    label: Optional[str] = None
    description: Optional[str] = None


class ColumnModel(CustomModel):
    name: str
    data_type: str


class RelationModel(CustomModel):
    """A pointer to a physical table or a view"""
    key: str
    # the database schema
    database_schema: str
    # the view_name or table_name
    reference: str
    relation_type: Literal["view", "table"]
    columns: List[ColumnModel]


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


class QueryContextModel(CustomModel):
    key: str
    joins: List[JoinModel] = []


class SemanticLayerModel(CustomModel):
    metrics: List[MetricModel] = []
    dimension: List[DimensionModel] = []
    joins: List[JoinModel] = []
    query_contexts: List[QueryContextModel] = []
    folders: List[FolderModel] = []
    filters: List[FilterModel] = []

    relations: List[RelationModel] = []

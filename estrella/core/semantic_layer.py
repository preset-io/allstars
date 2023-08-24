import glob
import os

from typing import Any, List, Literal, Optional
from dataclasses import dataclass, field
from estrella.models import SemanticLayerModel, RelationModel, ColumnModel
from sqlalchemy import MetaData, Table, inspect

from pydantic import BaseModel, Field, Json

BASE_FOLDER = "/tmp/estrella"

class Pydanticable:
    pydantic_model_class = None

    def to_pydantic(self):
        attrs = set(self.pydantic_model_class.__annotations__.keys())
        kwargs = {attr: getattr(self, attr) for attr in attrs}
        return self.pydantic_model_class(**kwargs)

    @classmethod
    def from_pydantic(cls, model):
        attrs = list(cls.pydantic_model_class.__annotations__.keys())
        kwargs = {attr: getattr(model, attr) for attr in attrs}
        return cls(
            name=model.name,
            data_type=model.data_type,
        )


@dataclass
class Column(Pydanticable):
    pydantic_model_class = ColumnModel

    name: str
    data_type: str


@dataclass
class Relation(Pydanticable):
    """A pointer to a physical table or a view"""
    pydantic_model_class = RelationModel


    # the database schema
    database_schema: str
    # the view_name or table_name
    reference: str
    columns: List[Column]

    relation_type: Literal["view", "table"]

    @property
    def key(self):
        return f"{self.database_schema}.{self.reference}"

    @classmethod
    def from_pydantic(cls, model):
        return cls(
            database_schema=model.database_schema,
            reference=model.reference,
            relation_type=model.relation_type,
            columns=[Column.from_pydantic(c) for c in model.columns],
        )


@dataclass
class SemanticLayer:
    relations: Optional[List[Relation]] = field(default_factory=list)
    #join
    #metrics
    #dimensions
    #contexts
    #filters
    #hierarchies
    #folders


    def create_relation(self, name, relation_type, columns, schema):
        return Relation(
            database_schema=schema,
            reference=name,
            columns=[
                Column(name=col["name"], data_type=str(col["type"])) for col in columns
            ],
            relation_type=relation_type,
        )

    def load_relations_from_schema(self, schema, sqla_engine):
        # create an inspector
        inspector = inspect(sqla_engine)

        # get all table names in the specified schema
        tables = inspector.get_table_names(schema=schema)

        # get all view names in the specified schema
        views = inspector.get_view_names(schema=schema)

        # iterate over tables and views, and populate the relations attribute
        rels = [(s, "table") for s in tables] + [(s, "view") for s in views]
        for name, relation_type in rels[:10]:
            print((name, relation_type))
            columns = inspector.get_columns(name, schema=schema)
            self.relations += [
                self.create_relation(name, relation_type, columns, schema)
            ]

    def to_pydantic(self):
        model = SemanticLayerModel(relations=[r.to_pydantic() for r in self.relations])
        return model

    def compile_to_files(self):

        # should move to some project init thing
        os.makedirs(os.path.join(BASE_FOLDER, 'relations'), exist_ok=True)

        for rel in self.relations:
            filename = os.path.join(BASE_FOLDER, 'relations', f"{rel.key}.yaml")
            rel.to_pydantic().to_yaml_file(filename)

    @classmethod
    def from_folder(cls, folder_path=None):
        rel_folder = folder_path or os.path.join(BASE_FOLDER, 'relations')
        yaml_files = glob.glob(f'{rel_folder}/*.yaml')
        relations = []
        for file_path in yaml_files:
            relations += [RelationModel.from_yaml_file(file_path)]

        return cls(
            relations=relations,
        )

    def infer_joins(self):
        """populates self.joins with Join objects based on self.relations!"""
        raise NotImplementedError()

    def infer_metrics(self):
        """populates self.metrics with Metric objects!"""
        raise NotImplementedError()

    def augment_joins(self):
        """read the local project to find joins"""
        raise NotImplementedError()

    def augment_metrics(self):
        """read the local project to find user-defined metrics"""
        raise NotImplementedError()

    def get_relations(object_list):
        """read the local project to find user-defined metrics"""
        raise NotImplementedError()

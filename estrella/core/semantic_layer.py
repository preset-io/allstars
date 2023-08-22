import os

from typing import Any, List, Literal, Optional
from dataclasses import dataclass
from estrella.models import SemanticLayerModel, RelationModel, ColumnModel
from sqlalchemy import MetaData, Table, inspect

from pydantic import BaseModel, Field, Json


@dataclass
class Column:
    name: str
    data_type: str

    def to_pydantic(self):
        return ColumnModel(name=self.name, data_type=self.data_type)


@dataclass
class Relation:
    """A pointer to a physical table or a view"""

    # the database schema
    database_schema: str
    # the view_name or table_name
    reference: str
    columns: List[Column]

    relation_type: Literal["view", "table"]

    @property
    def key(self):
        return f"{self.database_schema}.{self.reference}"

    def to_pydantic(self):
        return RelationModel(
            key=self.key,
            database_schema=self.database_schema,
            reference=self.reference,
            relation_type=self.relation_type,
            columns=[c.to_pydantic() for c in self.columns],
        )


@dataclass
class SemanticLayer:
    relations: List[Relation]

    def __init__(self):
        self.relations = []

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
        BASE_FOLDER = "/tmp/estrella"

        # should move to some project init thing
        os.makedirs(os.path.join(BASE_FOLDER, 'relations'), exist_ok=True)

        for rel in self.relations:
            filename = os.path.join(BASE_FOLDER, 'relations', f"{rel.key}.yaml")
            rel.to_pydantic().to_yaml_file(filename)

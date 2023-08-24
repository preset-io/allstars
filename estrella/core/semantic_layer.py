import glob
import os
import yaml

from typing import Any, List, Literal, Optional
from dataclasses import dataclass, field, asdict

from sqlalchemy import MetaData, Table, inspect

from estrella.core.relation import Column, Relation
from estrella.core.base import Serializable
from estrella.core.hierarchy import Hierarchy
from estrella.core.menu_items import Metric, Dimension, Filter, Folder
from estrella.core.query_context import QueryContext
from estrella.core.join import Join


@dataclass
class SemanticLayer(Serializable):

    # Menu items, things users will interact with
    metrics: List[Metric] = field(default_factory=list)
    dimension: List[Dimension] = field(default_factory=list)
    folders: List[Folder] = field(default_factory=list)

    # Internals
    relations: Optional[List[Relation]] = field(default_factory=list)
    joins: List[Join] = field(default_factory=list)
    query_contexts: List[QueryContext] = field(default_factory=list)
    filters: List[Filter] = field(default_factory=list)
    hierarchies: List[Hierarchy] = field(default_factory=list)

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
        for name, relation_type in rels[:5]:
            print((name, relation_type))
            columns = inspector.get_columns(name, schema=schema)
            self.relations += [
                self.create_relation(name, relation_type, columns, schema)
            ]

    def compile_to_files(self, folder):
        # should move to some project init thing
        os.makedirs(os.path.join(folder, "relations"), exist_ok=True)

        for rel in self.relations:
            filename = os.path.join(folder, "relations", f"{rel.key}.yaml")
            rel.to_yaml_file(filename)

    @classmethod
    def from_folder(cls, folder_path=None):
        rel_folder = folder_path
        yaml_files = glob.glob(f"{rel_folder}/*.yaml")
        print(rel_folder)
        relations = []
        for file_path in yaml_files:
            relations += [Relation.from_yaml_file(file_path)]

        return cls(
            relations=relations,
        )

    def get_relation_keys_for_objects(self, objects):
        relation_keys = set()
        for o in objects:
            relation_keys |= set(o.relation_keys)
        return relation_keys

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

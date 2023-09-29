import glob
import os
import yaml

from typing import Any, List, Literal, Optional
from dataclasses import dataclass, field, asdict
from itertools import combinations

from sqlalchemy import MetaData, Table, inspect

from estrella.core.relation import Column, Relation
from estrella.core.base import Serializable, SerializableCollection
from estrella.core.hierarchy import Hierarchy
from estrella.core.metric import Metric
from estrella.core.dimension import Dimension
from estrella.core.filter import Filter
from estrella.core.folder import Folder
from estrella.core.query_context import QueryContext
from estrella.core.join import Join


@dataclass
class SemanticLayer(Serializable):
    # Menu items, things users will interact with
    metrics: SerializableCollection[Metric] = field(default_factory=SerializableCollection)
    folders: SerializableCollection[Folder] = field(default_factory=SerializableCollection)
    dimensions: SerializableCollection[Dimension] = field(default_factory=SerializableCollection)

    # Internals
    relations: Optional[SerializableCollection[Relation]] = field(default_factory=SerializableCollection)
    joins: SerializableCollection[Join] = field(default_factory=SerializableCollection)
    query_contexts: SerializableCollection[QueryContext] = field(default_factory=SerializableCollection)
    filters: SerializableCollection[Filter] = field(default_factory=SerializableCollection)
    hierarchies: SerializableCollection[Hierarchy] = field(default_factory=SerializableCollection)

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

        relations = []
        for name, relation_type in rels:
            print((name, relation_type))
            columns = inspector.get_columns(name, schema=schema)
            relations.append(
                self.create_relation(name, relation_type, columns, schema)
            )
        self.relations = SerializableCollection(relations)

        self.infer_joins()
        self.infer_metrics()
        self.infer_dimensions()

    def compile_to_files(self, folder):
        # relations
        os.makedirs(os.path.join(folder, "relations"), exist_ok=True)
        for rel in self.relations:
            filename = os.path.join(folder, "relations", f"{rel.key}.yaml")
            rel.to_yaml_file(filename)

        # joins
        filename = os.path.join(folder, "joins.yaml")
        self.joins.to_yaml_file(filename, wrap_under="joins")

        # metrics
        filename = os.path.join(folder, "metrics.yaml")
        self.metrics.to_yaml_file(filename, wrap_under="metrics")

        # dimensions
        filename = os.path.join(folder, "dimensions.yaml")
        self.dimensions.to_yaml_file(filename, wrap_under="dimensions")

    @classmethod
    def from_folder(cls, folder_path=None):

        # Relations
        rel_folder = os.path.join(folder_path, "relations")
        yaml_files = glob.glob(f"{rel_folder}/*.yaml")
        relations = SerializableCollection()
        for file_path in yaml_files:
            relations.append(Relation.from_yaml_file(file_path))

        # Joins
        f = os.path.join(folder_path, "joins.yaml")
        joins = SerializableCollection.from_yaml_file(f, Join, key="joins")

        # Metrics
        f = os.path.join(folder_path, "metrics.yaml")
        metrics = SerializableCollection.from_yaml_file(f, Metric, key="metrics")

        # Dimensions
        f = os.path.join(folder_path, "dimensions.yaml")
        dimensions = SerializableCollection.from_yaml_file(f, Dimension, key="dimensions")

        # Folders
        f = os.path.join(folder_path, "folders.yaml")
        folders = SerializableCollection.from_yaml_file(f, Folder, key="folders")
        expanded_folders = SerializableCollection()
        for folder in folders:
            folder.flatten(expanded_folders)

        return cls(
            relations=relations,
            joins=joins,
            dimensions=dimensions,
            metrics=metrics,
            folders=expanded_folders,
        )

    def upsert(self, semantic_layer):
        """Insert new keys and update existing ones"""
        for collection in ['relations', 'metrics', 'dimensions']:
            d1 = getattr(self, collection)
            d2 = getattr(semantic_layer, collection)
            d1.upsert(d2)

    def get_relation_keys_for_objects(self, objects):
        relation_keys = set()
        for o in objects:
            relation_keys |= set(o.relation_keys)
        return relation_keys

    def infer_metrics(self):
        """populates self.metrics with Metric objects!"""
        metrics = SerializableCollection()
        for r in self.relations:
            metrics.append(
                Metric(
                    key=f"{r.key}.count",
                    label=f"{r.reference} count",
                    description="the number of {r.reference}",
                    expression="COUNT(*)",
                    relation_key=r.key,
                )
            )
        self.metrics = metrics

    def infer_dimensions(self):
        """populates self.metrics with Dimensions objects!"""
        dims = SerializableCollection()
        for r in self.relations:
            for c in r.columns:
                dims.append(
                    Dimension(
                        key=f"{r.key}.{c.name}",
                        expression=f"{r.key}.{c.name}",
                        relation_key=r.key,
                    )
                )
        self.dimensions = dims

    def infer_joins(self, exclude_views=True):
        """
        TODO this should grow quite a bit, inferring joins is quite a complex
        and core feature. Some thoughts:

        - should look at PKs and FKs, cardinality
        - look for common columns where left looks like a PK
        - should we scan/look for unicity?
        - hints? look for column or table description that says pk or fk?
        - be careful around overriding enriched stuff, if users have already
          defined a join between two tables, do not try to suggest another one
          unless they're asking to --overwrite
        """
        self.joins = SerializableCollection()
        relations = []
        joins = []
        for r in self.relations:
            if not exclude_views or (exclude_views and r.relation_type != "view"):
                relations.append(r)

        for r, fr in combinations(relations, 2):
            if not r == fr:
                cols = r.find_common_columns(fr)
                col_names = {c.name for c in cols}
                if col_names == {"customer_id"}:
                    # TODO more work here
                    joins.append(r.gen_join(fr, cols))

        self.joins = SerializableCollection(joins)

    def augment_joins(self):
        """read the local project to find joins"""
        raise NotImplementedError()

    def augment_metrics(self):
        """read the local project to find user-defined metrics"""
        raise NotImplementedError()

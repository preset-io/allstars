from dataclasses import dataclass
import os

from sqlalchemy import create_engine

from estrella import config
from estrella.core.semantic_layer import SemanticLayer


class Project:
    semantic_layer: SemanticLayer

    def __init__(self, folder=None, sqla_conn=None, *args, **kwargs):
        self.folder = folder or config.ESTRELLA_FOLDER
        self.sqla_conn = sqla_conn or config.ESTRELLA_SQLA_CONN

        self.engine = create_engine(
            self.sqla_conn, credentials_path="/Users/max/.dbt/dev-dbt.json"
        )

    def load(self, database_schema=None):
        if database_schema:
            self.semantic_layer = SemanticLayer()
            self.semantic_layer.load_relations_from_schema(database_schema, self.engine)
        else:
            relation_folder = self.folder
            self.semantic_layer = SemanticLayer.from_folder(relation_folder)

    def flush(self):
        self.semantic_layer.compile_to_files(self.folder)

from dataclasses import dataclass
import os

from allstars import config
from allstars.core.semantic_layer import SemanticLayer
from allstars.database_interface import DatabaseInterface


class Project:
    semantic_layer: SemanticLayer

    def __init__(self, folder=None, sqla_conn=None, *args, **kwargs):
        self.folder = folder or config.ALLSTARS_FOLDER
        self.sqla_conn = sqla_conn or config.ALLSTARS_SQLA_CONN

        self.db = DatabaseInterface(self.sqla_conn)

    def load(self, database_schema=None):
        if database_schema:
            self.semantic_layer = SemanticLayer()
            self.semantic_layer.load_relations_from_schema(database_schema, self.db)
        else:
            relation_folder = self.folder
            self.semantic_layer = SemanticLayer.from_folder(relation_folder)

    def flush(self):
        self.semantic_layer.compile_to_files(self.folder)

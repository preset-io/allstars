from dataclasses import dataclass
import os

from sqlalchemy import create_engine

from estrella.core.semantic_layer import SemanticLayer


@dataclass
class Project:
    semantic_layer: SemanticLayer

    BASE_FOLDER: str = "/tmp/estrella"
    SQLA_CON: str = "bigquery://preset-cloud-dev-dbt/core"


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = create_engine(self.SQLA_CON, credentials_path="/Users/max/.dbt/dev-dbt.json")

    def load(self, database_schema=None):
        if database_schema:
            self.semantic_layer = SemanticLayer()
            self.semantic_layer.load_relations_from_schema(database_schema, self.engine)
        else:
            relation_folder = os.path.join(self.BASE_FOLDER, "relations")
            self.semantic_layer = SemanticLayer.from_folder(relation_folder)

    def flush(self):
        self.semantic_layer.compile_to_files(self.BASE_FOLDER)

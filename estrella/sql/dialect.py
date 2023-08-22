from types import ModuleType

from sqlalchemy.dialects.sqlite.base import SQLiteDialect

from estrella.sql import db


class EstrellaDialect(SQLiteDialect):
    name = "estrella"

    @classmethod
    def dbapi(cls) -> ModuleType:
        return db

"""
SQLAlchemy dialect.
"""

from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, TypedDict

import sqlalchemy.types
from sqlalchemy.engine.base import Connection as SqlaConnection
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.engine.url import URL
from sqlalchemy.sql import compiler
from sqlalchemy.sql.type_api import TypeEngine

from estrella.sql import dbapi
from estrella.sql.dbapi.connection import Connection
from estrella.sql.dbapi.typing import ColumnType


class SQLAlchemyColumn(TypedDict):
    """
    A custom type for a SQLAlchemy column.
    """

    name: str
    type: TypeEngine
    nullable: bool
    default: Optional[str]
    autoincrement: str
    primary_key: int


def get_sqla_type(type_: ColumnType) -> TypeEngine:
    """
    Convert from Estrella to SQLA type.
    """
    type_map = {
        ColumnType.BYTES: sqlalchemy.types.BINARY,
        ColumnType.STR: sqlalchemy.types.TEXT,
        ColumnType.FLOAT: sqlalchemy.types.FLOAT,
        ColumnType.INT: sqlalchemy.types.INT,
        ColumnType.DECIMAL: sqlalchemy.types.DECIMAL,
        ColumnType.BOOL: sqlalchemy.types.BOOLEAN,
        ColumnType.DATETIME: sqlalchemy.types.DATETIME,
        ColumnType.DATE: sqlalchemy.types.DATE,
        ColumnType.TIME: sqlalchemy.types.TIME,
        # imperfect matches
        ColumnType.TIMEDELTA: sqlalchemy.types.TEXT,
        ColumnType.LIST: sqlalchemy.types.ARRAY,
        ColumnType.DICT: sqlalchemy.types.JSON,
    }
    return type_map[type_]()


class EstrellaDialect(DefaultDialect):
    """
    A SQLAlchemy dialect for Estrella.
    """

    name = "estrella"
    driver = ""

    statement_compiler = compiler.SQLCompiler
    ddl_compiler = compiler.DDLCompiler
    type_compiler = compiler.GenericTypeCompiler
    preparer = compiler.IdentifierPreparer

    supports_alter = False
    supports_comments = True
    inline_comments = True
    supports_statement_cache = True

    supports_schemas = False
    supports_views = False
    postfetch_lastrowid = False

    supports_native_boolean = True

    isolation_level = "AUTOCOMMIT"

    default_paramstyle = "pyformat"

    supports_is_distinct_from = False

    def __init__(self, database_uri: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.database_uri = database_uri

    @classmethod
    def import_dbapi(cls) -> ModuleType:  # pylint: disable=method-hidden
        """
        Return the DB API module.
        """
        return dbapi

    dbapi = import_dbapi

    def create_connect_args(
        self,
        url: URL,
    ) -> Tuple[Tuple[str], Dict[str, Any]]:
        return (self.database_uri,), {}

    def do_ping(self, dbapi_connection: Connection) -> bool:
        """
        Is the service up?
        """
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
        except Exception:  # pylint: disable=broad-except
            return False

        return True

    def has_table(
        self,
        connection: SqlaConnection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> bool:
        """
        Return if a given table exists.
        """
        return table_name == "super"

    def get_table_names(
        self,
        connection: SqlaConnection,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> List[str]:
        """
        Return a list of table names.
        """
        return ["super"]

    def get_columns(
        self,
        connection: SqlaConnection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> List[SQLAlchemyColumn]:
        """
        Return information about columns.
        """
        return []

    def do_rollback(self, dbapi_connection: Connection) -> None:
        """
        Estrella doesn't support rollbacks.
        """

    def get_schema_names(self, connection: SqlaConnection, **kw: Any):
        """
        Return the list of schemas.
        """
        return ["main"]

    def get_pk_constraint(
        self,
        connection: SqlaConnection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ):
        return {"constrained_columns": [], "name": None}

    def get_foreign_keys(
        self,
        connection: SqlaConnection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ):
        return []

    get_check_constraints = get_foreign_keys
    get_indexes = get_foreign_keys
    get_unique_constraints = get_foreign_keys

    def get_table_comment(self, connection, table_name, schema=None, **kwargs):
        return {"text": ""}

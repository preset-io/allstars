"""
An implementation of the DB API 2.0.
"""

from estrella.sql.dbapi.connection import connect
from estrella.sql.dbapi.exceptions import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)
from estrella.sql.dbapi.types import (
    BINARY,
    DATETIME,
    NUMBER,
    STRING,
    Binary,
    Date,
    DateFromTicks,
    Time,
    TimeFromTicks,
    Timestamp,
    TimestampFromTicks,
)

apilevel = "2.0"
threadsafety = 3
paramstyle = "pyformat"

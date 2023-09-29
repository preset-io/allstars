"""
An implementation of the DB API 2.0.
"""

from allstars.sql.dbapi.connection import connect
from allstars.sql.dbapi.exceptions import (
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
from allstars.sql.dbapi.types import (
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

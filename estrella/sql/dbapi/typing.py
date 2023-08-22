"""
Type annotations for the DB API 2.0 implementation.
"""

from enum import Enum
from typing import List, Optional, Tuple

# Cursor description
Description = Optional[
    List[
        Tuple[
            str,
            ColumnType,
            Optional[str],
            Optional[str],
            Optional[str],
            Optional[str],
            Optional[bool],
        ]
    ]
]


class ColumnType(str, Enum):
    """
    Types for columns.

    These represent the values from the ``python_type`` attribute in SQLAlchemy columns.
    """

    BYTES = "BYTES"
    STR = "STR"
    FLOAT = "FLOAT"
    INT = "INT"
    DECIMAL = "DECIMAL"
    BOOL = "BOOL"
    DATETIME = "DATETIME"
    DATE = "DATE"
    TIME = "TIME"
    TIMEDELTA = "TIMEDELTA"
    LIST = "LIST"
    DICT = "DICT"


class TypeEnum(str, Enum):
    """
    PEP 249 basic types.
    Unfortunately SQLAlchemy doesn't seem to offer an API for determining the types of the # E: line too long (90 > 88 characters)
    columns in a (SQL Core) query, and the DB API 2.0 cursor only offers very coarse
    types.
    """

    STRING = "STRING"
    BINARY = "BINARY"
    NUMBER = "NUMBER"
    DATETIME = "DATETIME"
    UNKNOWN = "UNKNOWN"

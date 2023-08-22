"""
An implementation of a DB API 2.0 cursor.
"""
# pylint: disable=invalid-name

import itertools
from typing import Any, Dict, Iterator, List, Optional, Tuple

from yarl import URL

from estrella.sql.dbapi.decorators import check_closed, check_result
from estrella.sql.dbapi.exceptions import NotSupportedError
from estrella.sql.dbapi.typing import Description
from estrella.sql.dbapi.utils import escape_parameter


class Cursor:

    """
    Connection cursor.
    """

    def __init__(self, base_url: URL):
        self.base_url = base_url

        self.arraysize = 1
        self.closed = False
        self.description: Description = None

        self._results: Optional[Iterator[Tuple[Any, ...]]] = None
        self._rowcount = -1

    @property  # type: ignore
    @check_closed
    def rowcount(self) -> int:
        """
        Return the number of rows after a query.
        """
        try:
            results = list(self._results)  # type: ignore
        except TypeError:
            return -1

        n = len(results)
        self._results = iter(results)
        return max(0, self._rowcount) + n

    @check_closed
    def close(self) -> None:
        """
        Close the cursor.
        """
        self.closed = True

    @check_closed
    def execute(
        self,
        operation: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> "Cursor":
        """
        Execute a query using the cursor.
        """
        self.description = None
        self._rowcount = -1

        if parameters:
            escaped_parameters = {
                key: escape_parameter(value) for key, value in parameters.items()
            }
            operation %= escaped_parameters

        # XXX transpile query
        # XXX execute query and read results
        rows = []

        self._results = (tuple(row) for row in rows)
        # self.description = [...]

        return self

    @check_closed
    def executemany(
        self,
        operation: str,
        seq_of_parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> "Cursor":
        """
        Execute multiple statements.

        Currently not supported.
        """
        raise NotSupportedError(
            "``executemany`` is not supported, use ``execute`` instead",
        )

    @check_result
    @check_closed
    def fetchone(self) -> Optional[Tuple[Any, ...]]:
        """
        Fetch the next row of a query result set, returning a single sequence,
        or ``None`` when no more data is available.
        """
        try:
            row = self.next()
        except StopIteration:
            return None

        self._rowcount = max(0, self._rowcount) + 1

        return row

    @check_result
    @check_closed
    def fetchmany(self, size=None) -> List[Tuple[Any, ...]]:
        """
        Fetch the next set of rows of a query result, returning a sequence of
        sequences (e.g. a list of tuples). An empty sequence is returned when
        no more rows are available.
        """
        size = size or self.arraysize
        results = list(itertools.islice(self, size))

        return results

    @check_result
    @check_closed
    def fetchall(self) -> List[Tuple[Any, ...]]:
        """
        Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples). Note that the cursor's
        arraysize attribute can affect the performance of this operation.
        """
        results = list(self)

        return results

    @check_closed
    def setinputsizes(self, sizes: int) -> None:
        """
        Used before ``execute`` to predefine memory areas for parameters.

        Currently not supported.
        """

    @check_closed
    def setoutputsizes(self, sizes: int) -> None:
        """
        Set a column buffer size for fetches of large columns.

        Currently not supported.
        """

    @check_result
    @check_closed
    def __iter__(self) -> Iterator[Tuple[Any, ...]]:
        for row in self._results:  # type: ignore
            self._rowcount = max(0, self._rowcount) + 1
            yield row

    @check_result
    @check_closed
    def __next__(self) -> Tuple[Any, ...]:
        return next(self._results)  # type: ignore

    next = __next__

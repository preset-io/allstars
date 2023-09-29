import pytest
from sqlalchemy.engine import Engine

from allstars.sql.transpile import transpile


@pytest.mark.parametrize(
    "semantic_query, actual_query",
    [
        #        (
        #            """
        # SELECT sum("sales.price") AS "SUM(sales.price)"
        # FROM main.super
        # ORDER BY "SUM(sales.price)" DESC
        # LIMIT 100;
        #            """,
        #            (
        #                'SELECT SUM(sales.price) AS "SUM(sales.price)" FROM sales '
        #                "ORDER BY SUM(sales.price) DESC LIMIT 100"
        #            ),
        #        ),
        (
            """
SELECT "dim_user.country" AS "dim_user.country",
       sum("sales.price") AS "SUM(sales.price)"
FROM main.super
GROUP BY "dim_user.country"
ORDER BY "SUM(sales.price)" DESC
LIMIT 100;
            """,
            (
                'SELECT dim_user.country AS "dim_user.country", '
                'SUM(sales.price) AS "SUM(sales.price)" '
                "FROM sales JOIN dim_user ON sales.user_id = dim_user.id "
                "GROUP BY dim_user.country ORDER BY SUM(sales.price) DESC LIMIT 100"
            ),
        ),
    ],
)
def test_transpile(engine: Engine, semantic_query: str, actual_query: str) -> None:
    """
    Simple tests.
    """
    assert transpile(engine, semantic_query) == actual_query

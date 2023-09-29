import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@pytest.fixture
def engine() -> Engine:
    """
    Create an SQL All ⭐ Stars DB on top of SQLite.
    """
    os.unlink("test.db")
    engine = create_engine("sqlite:///test.db")
    connection = engine.connect()
    connection.execute(
        text(
            """
            CREATE TABLE dim_user (
                id INTEGER PRIMARY KEY,
                name TEXT,
                country TEXT
            )"""
        )
    )
    connection.execute(text("INSERT INTO dim_user VALUES (1, 'Alice', 'US')"))
    connection.execute(text("INSERT INTO dim_user VALUES (2, 'Bob', 'CA')"))
    connection.execute(
        text(
            """
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                price INTEGER,
                FOREIGN KEY(user_id) REFERENCES dim_user(id)
            )"""
        )
    )
    connection.execute(text("INSERT INTO sales VALUES (1, 1, 42)"))
    connection.execute(text("INSERT INTO sales VALUES (2, 2, 100)"))
    connection.commit()

    return engine

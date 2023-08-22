from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlglot import exp, parse, parse_one
from sqlglot.dialects.dialect import Dialect

from estrella.sql.dbapi.exceptions import ProgrammingError


def transpile(engine: Engine, query: str) -> str:
    """
    Transpile a semantic layer query.
    """
    inspector = inspect(engine)
    tree = parse(query)

    # analyze tables
    tables = set()
    for statement in tree:
        for table in statement.find_all(exp.Table):
            tables.add(table.name)

    if tables != {"super"}:
        raise ProgrammingError("Only the 'super' table is supported")

    # fetch all column references
    statements = []
    for statement in tree:
        columns = set()
        for column in statement.find_all(exp.Column):
            columns.add(column.name)
            # replace column reference with actual column name
            column.replace(parse_one(column.name))

        # figure out how to join tables
        tables = {table.split(".")[0] for table in columns}
        if len(tables) == 1:
            replacement = parse_one(tables.pop(), into=exp.Table)
        elif len(tables) == 2:
            for table in tables:
                fks = [
                    fk
                    for fk in inspector.get_foreign_keys(table_name=table)
                    if fk["referred_table"] in tables and fk["referred_table"] != table
                ]
                if not fks:
                    continue
                if len(fks) > 1:
                    raise NotImplementedError(f"Can't join between tables: {tables}")
                fk = fks.pop()
                constrained_columns = fk["constrained_columns"]
                referred_table = fk["referred_table"]
                referred_columns = fk["referred_columns"]

                replacement = parse_one(table, into=exp.Table)
                statement = statement.join(
                    referred_table,
                    on=" AND ".join(
                        f"{table}.{constrained_column} = {referred_table}.{referred_column}"
                        for constrained_column, referred_column in zip(
                            constrained_columns, referred_columns
                        )
                    ),
                )
                break
            else:
                raise NotImplementedError(f"Can't join between tables: {tables}")
        else:
            raise NotImplementedError("Only one or two tables are supported")

        super = statement.find(exp.Table)
        super.replace(replacement)

        statements.append(statement)

    query = ";\n".join(
        Dialect.get_or_raise("sqlite")().generate(statement) for statement in statements
    )

    return query

from sqlalchemy import create_engine, MetaData, Table, inspect


class DatabaseInterface:
    def __init__(self, sqla_conn):
        self.sqla_conn = sqla_conn
        self.engine = create_engine(
            self.sqla_conn, credentials_path="/Users/max/.dbt/dev-dbt.json"
        )
        self.inspector = inspect(self.engine)

    def get_df(self, sql):
        """get a dataframe!"""

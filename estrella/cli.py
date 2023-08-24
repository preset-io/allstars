import click
from estrella.core import SemanticLayer

@click.group()
def cli():
    pass

@click.command()
@click.argument('schema')
def extract(schema):
    click.echo(f'Extracting metadata from schema: {schema}')
    sl = SemanticLayer()

    from sqlalchemy import create_engine
    conn = "bigquery://preset-cloud-dev-dbt/core"
    eng = create_engine(conn, credentials_path="/Users/max/.dbt/dev-dbt.json")

    sl = SemanticLayer()

    sl.load_relations_from_schema(schema, eng)
    sl.compile_to_files()


@click.command()
def read():
    sl = SemanticLayer.from_folder()
    for rel in sl.relations:
        print(rel.to_pydantic().to_yaml())

cli.add_command(extract)
cli.add_command(read)

def run() -> None:
    cli()
    print("Running!")

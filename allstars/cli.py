import click
from sqlalchemy import create_engine

from allstars.core.project import Project


@click.group()
def cli():
    pass


@click.command()
@click.argument("schema")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files.")
def extract(schema, overwrite):
    click.echo(f"Extracting metadata from schema: {schema}")

    extracted_project = Project()
    extracted_project.load(schema)

    if not overwrite:
        current_project = Project()
        current_project.load()
        extracted_project.semantic_layer.upsert(current_project.semantic_layer)

    extracted_project.flush()


@click.command()
@click.option("--key", default=None)
def read(key):
    project = Project()
    project.load()
    sl = project.semantic_layer

    print(sl.to_yaml(key=key))


@click.command()
@click.argument("sql")
def sql(sql):
    project = Project()
    project.load()
    project.semantic_layer

    transpiled_sql = Transpiler.transpile(sql)

    results = DatabaseInterface.get_df(sql)
    print(results)


cli.add_command(extract)
cli.add_command(read)


def run() -> None:
    cli()
    print("Running!")

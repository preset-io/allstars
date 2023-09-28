import click
from sqlalchemy import create_engine

from estrella.core.project import Project


@click.group()
def cli():
    pass


@click.command()
@click.argument("schema")
def extract(schema):
    click.echo(f"Extracting metadata from schema: {schema}")

    project = Project()
    project.load(schema)
    project.flush()


@click.command()
def read():
    project = Project()
    project.load()
    sl = project.semantic_layer
    print(sl.to_yaml())


cli.add_command(extract)
cli.add_command(read)


def run() -> None:
    cli()
    print("Running!")

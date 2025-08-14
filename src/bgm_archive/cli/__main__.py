import click
import dotenv
import logging
from .validate_archive import validate_wiki_archive
from .import_es import import_es
from .import_duckdb import import_duckdb
from .fastapi import fastapi_server


@click.group()
def cli():
    """Bangumi Archive CLI tools."""
    pass


# Register commands
cli.add_command(validate_wiki_archive)
cli.add_command(import_es)
cli.add_command(import_duckdb)
cli.add_command(fastapi_server)

if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s - %(funcName)s: %(message)s",
    )
    cli()

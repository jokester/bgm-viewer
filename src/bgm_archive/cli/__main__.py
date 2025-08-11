import click
import dotenv
from .validate_archive import validate_wiki_archive
from .import_es import import_es
from .import_duckdb import import_duckdb


@click.group()
def cli():
    """Bangumi Archive CLI tools."""
    pass


# Register commands
cli.add_command(validate_wiki_archive)
cli.add_command(import_es)
cli.add_command(import_duckdb)


if __name__ == "__main__":
    dotenv.load_dotenv()
    cli()

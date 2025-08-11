import click
import dotenv
from .validate_archive import validate_wiki_archive
from .import_es import import_es


@click.group()
def cli():
    """Bangumi Archive CLI tools."""
    pass


# Register commands
cli.add_command(validate_wiki_archive)
cli.add_command(import_es)


if __name__ == "__main__":
    dotenv.load_dotenv()
    cli()

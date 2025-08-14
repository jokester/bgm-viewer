from typing import Iterable, Iterator
import click
import tqdm
import concurrent.futures as cf
from pathlib import Path
from collections import Counter

from bgm_archive.loader.wiki_archive_loader import WikiArchiveLoader
from bgm_archive.duckdb import DuckdbStorage


@click.command("import-duckdb")
@click.argument("archive", type=click.Path(exists=True, path_type=Path))
@click.argument("db", type=click.Path(path_type=Path))
@click.option("--limit", type=int, help="Limit the number of records to import")
def import_duckdb(archive: Path, db: Path, limit: int = None):
    """
    Import data from a wiki archive into a DuckDB database.
    """
    bg = DuckdbStorage(db=db)
    bg.setup_db()

    loader = WikiArchiveLoader(archive_path=archive)
    bg.load_all(loader, limit=limit, progress_bar=True)

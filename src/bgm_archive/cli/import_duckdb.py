from typing import Iterable, Iterator
import click
import tqdm
import concurrent.futures as cf
from pathlib import Path
from collections import Counter

from bgm_archive.loader.wiki_archive_loader import WikiArchiveLoader
from bgm_archive.graph import BgmGraph


@click.command("import-duckdb")
@click.argument("archive", type=click.Path(exists=True, path_type=Path))
@click.argument("db", type=click.Path(path_type=Path))
def import_duckdb(archive: Path, db: Path):
    """
    Import data from a wiki archive into a DuckDB database.
    """
    bg = BgmGraph(path=db)
    bg.setup_db()
    bg.create_bgm_schema()

    loader = WikiArchiveLoader(archive_path=archive)
    bg.import_all(loader, limit=None, progress_bar=True)

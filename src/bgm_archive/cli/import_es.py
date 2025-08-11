import click
from pathlib import Path
from bgm_archive.loader.wiki_archive_loader import WikiArchiveLoader
from bgm_archive.es import get_async_client, SubjectsIndex
import tqdm
import asyncio
import itertools


@click.command("import-es")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def import_es(path: Path):
    es = get_async_client()
    loader = WikiArchiveLoader(str(path), stop_on_error=False)
    si = SubjectsIndex(es=es, index_name='bgm_subjects')

    async def main():
        await si.recreate_index()
        await si.add_documents(tqdm.tqdm(
            itertools.islice(loader.subjects(), 10),
            # loader.subjects()
        )
        )
        await es.close()

    asyncio.run(main())

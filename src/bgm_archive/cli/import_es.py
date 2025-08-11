from typing import Iterator
import click
from pathlib import Path
from bgm_archive.loader.wiki_archive_loader import WikiArchiveLoader
from bgm_archive.es import (
    get_async_client,
    SubjectsIndex,
    CharacterIndex,
    PersonIndex,
    EpisodeIndex,
)
from tqdm import tqdm
import asyncio
import itertools


# def tqdm(x): return x


@click.command("import-es")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def import_es(path: Path):
    es = get_async_client()
    loader = WikiArchiveLoader(str(path), stop_on_error=False)
    si = SubjectsIndex(es=es, index_name="bgm_subjects")
    ci = CharacterIndex(es=es, index_name="bgm_characters")
    pi = PersonIndex(es=es, index_name="bgm_persons")
    ei = EpisodeIndex(es=es, index_name="bgm_episodes")

    def wrap_stream(iterator: Iterator):
        # return tqdm(iterator)
        stop = None
        yield from tqdm(itertools.islice(iterator, stop))

    async def main():
        await si.recreate_index()
        await ci.recreate_index()
        await pi.recreate_index()
        await ei.recreate_index()

        await asyncio.gather(
            si.add_documents(wrap_stream(loader.subjects())),
            ci.add_documents(wrap_stream(loader.characters())),
            pi.add_documents(wrap_stream(loader.persons())),
            ei.add_documents(wrap_stream(loader.episodes())),
        )
        await es.close()

    asyncio.run(main())

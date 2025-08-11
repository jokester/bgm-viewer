from typing import Iterable
import click
import tqdm
import concurrent.futures as cf
from pathlib import Path
from collections import Counter
from bgm_archive.loader.wiki_archive_loader import WikiArchiveLoader


@click.command("validate-archive")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def validate_wiki_archive(path: Path):
    """
    Validate a Bangumi wiki archive by iterating through all entity types.

    Args:
        path: Path to the archive file

    Returns:
        Counter with counts of each entity type
    """
    loader = WikiArchiveLoader(str(path), stop_on_error=False)
    entity_counts = Counter()

    def work(*, position: int, desc: str, count_key: str, iterable: Iterable):
        for _ in tqdm.tqdm(iterable, desc=desc):
            entity_counts[count_key] += 1

    # not faster in the same process :rolling-eyes:
    with cf.ThreadPoolExecutor(max_workers=1) as executor:
        for index, (desc, count_key, iterable) in enumerate([
            ("Subjects", "subjects", loader.subjects()),
            ("Persons", "persons", loader.persons()),
            ("Characters", "characters", loader.characters()),
            ("Episodes", "episodes", loader.episodes()),
            ("Subject Relations", "subject_relations", loader.subject_relations()),
            ("Subject-Person Relations", "subject_persons", loader.subject_persons()),
            ("Subject-Character Relations",
             "subject_characters", loader.subject_characters()),
            ("Person-Character Relations",
             "person_characters", loader.person_characters())
        ]):
            executor.submit(work, position=0, desc=desc,
                            count_key=count_key, iterable=iterable)

    # Print summary
    print("\nValidation Summary:")
    for entity_type, count in entity_counts.items():
        print(f"  {entity_type}: {count} succeeded")

    all_errors = loader.get_validation_errors()
    for model_class, errors in all_errors.items():
        print(f"First validation errors for {model_class.__name__}:")
        for error in errors[:3]:
            print(f"  - {error}")
        problematic_values = set(ed["input"]
                                 for e in errors for ed in e.errors())
        print(f"  - input values: {problematic_values}")

    return entity_counts

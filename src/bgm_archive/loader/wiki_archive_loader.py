from collections import defaultdict
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, Type, TypeVar
import zipfile
from pydantic import BaseModel, ValidationError

from .model import (
    Subject,
    Person,
    Character,
    Episode,
    SubjectRelation,
    SubjectPerson,
    SubjectCharacter,
    PersonCharacter,
)

# Type variable for generic model handling
T = TypeVar("T", bound=BaseModel)

# Set up logging
logger = logging.getLogger(__name__)


class WikiArchiveLoader:
    """
    A loader to consume zipped jsonlines files, released at https://github.com/bangumi/Archive.

    This loader reads JSONL files from a zip archive, validates each entry with
    the appropriate Pydantic model, and yields the validated entries.

    The zip file is expected to have the following structure:
    - subject.jsonlines
    - person.jsonlines
    - character.jsonlines
    - episode.jsonlines
    - subject-relations.jsonlines
    - subject-persons.jsonlines
    - subject-characters.jsonlines
    - person-characters.jsonlines
    """

    # Mapping of file names to their corresponding Pydantic models
    FILE_MODEL_MAP: Dict[str, Type[BaseModel]] = {
        "subject.jsonlines": Subject,
        "person.jsonlines": Person,
        "character.jsonlines": Character,
        "episode.jsonlines": Episode,
        "subject-relations.jsonlines": SubjectRelation,
        "subject-persons.jsonlines": SubjectPerson,
        "subject-characters.jsonlines": SubjectCharacter,
        "person-characters.jsonlines": PersonCharacter,
    }

    def __init__(self, archive_path: Path | str, stop_on_error=True):
        """
        Initialize the loader with the path to the zip archive.

        Args:
            archive_path: Path to the zip archive containing JSONL files
        """
        self.__archive_path = archive_path
        self.__stop_on_error = stop_on_error
        self.__validation_errors: dict[type, list[ValidationError]] = defaultdict(list)

    @contextmanager
    def _open_archive(self):
        """
        Context manager for opening and closing the zip archive.

        Yields:
            The opened ZipFile object
        """
        yield zipfile.ZipFile(self.__archive_path, "r")

    def _load_entries(
        self,
        filename: str,
        model_class: Type[T],
    ) -> Iterator[T]:
        """
        Generic method to load and validate entries from a JSONL file in the zip archive.

        Args:
            filename: Name of the JSONL file in the zip archive
            model_class: Pydantic model class to validate entries against

        Yields:
            Validated model instances
        """

        with self._open_archive() as archive:
            try:
                with archive.open(filename) as file:
                    for line_number, line in enumerate(file):
                        try:
                            # Decode bytes to string and parse JSON
                            line_str = line.decode("utf-8").strip()
                            if not line_str:  # Skip empty lines
                                continue

                            validated_entry = model_class.model_validate_json(line_str)
                            yield validated_entry

                        except ValidationError as e:
                            if self.__stop_on_error:
                                raise
                            else:
                                self.__validation_errors[model_class].append(e)
                        except Exception as e:
                            logger.error(
                                f"Unexpected error processing {filename}:{line_number}: {e}"
                            )
                            raise
            except KeyError:
                logger.warning(f"File {filename} not found in archive")

    def subjects(self) -> Iterator[Subject]:
        """
        Load and validate Subject entries from the archive.

        Yields:
            Validated Subject instances
        """
        yield from self._load_entries("subject.jsonlines", Subject)

    def persons(self) -> Iterator[Person]:
        """
        Load and validate Person entries from the archive.

        Yields:
            Validated Person instances
        """
        yield from self._load_entries("person.jsonlines", Person)

    def characters(self) -> Iterator[Character]:
        """
        Load and validate Character entries from the archive.

        Yields:
            Validated Character instances
        """
        yield from self._load_entries("character.jsonlines", Character)

    def episodes(self) -> Iterator[Episode]:
        """
        Load and validate Episode entries from the archive.

        Yields:
            Validated Episode instances
        """
        yield from self._load_entries("episode.jsonlines", Episode)

    def subject_relations(self) -> Iterator[SubjectRelation]:
        """
        Load and validate SubjectRelation entries from the archive.

        Yields:
            Validated SubjectRelation instances
        """
        yield from self._load_entries("subject-relations.jsonlines", SubjectRelation)

    def subject_persons(self) -> Iterator[SubjectPerson]:
        """
        Load and validate SubjectPerson entries from the archive.

        Yields:
            Validated SubjectPerson instances
        """
        yield from self._load_entries("subject-persons.jsonlines", SubjectPerson)

    def subject_characters(self) -> Iterator[SubjectCharacter]:
        """
        Load and validate SubjectCharacter entries from the archive.

        Yields:
            Validated SubjectCharacter instances
        """
        yield from self._load_entries("subject-characters.jsonlines", SubjectCharacter)

    def person_characters(self) -> Iterator[PersonCharacter]:
        """
        Load and validate PersonCharacter entries from the archive.

        Yields:
            Validated PersonCharacter instances
        """
        yield from self._load_entries("person-characters.jsonlines", PersonCharacter)

    def load_all(self) -> Dict[str, Iterator[BaseModel]]:
        """
        Load all types of entries from the archive.

        Returns:
            Dictionary mapping file names to iterators of validated entries
        """
        return {
            file_name: self._load_entries(file_name, model_class)
            for file_name, model_class in self.FILE_MODEL_MAP.items()
        }

    def get_validation_errors(self) -> dict[type, list[ValidationError]]:
        """
        Get validation errors encountered during loading.

        Returns:
            Dictionary mapping model classes to lists of ValidationError instances
        """
        return dict(self.__validation_errors)

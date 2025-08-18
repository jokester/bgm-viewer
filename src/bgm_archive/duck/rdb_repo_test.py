import os
import duckdb
from .rdb_repo import RdbRepository

repo = RdbRepository(db=os.environ["TEST_DUCKDB"])


def test_find_subject_by_id():
    assert "connect" in dir(duckdb)

    # Test valid ID
    subject = repo.find_subject_by_id(1)
    assert subject is not None
    assert subject.id == 1
    assert hasattr(subject, "name")
    assert hasattr(subject, "type")
    assert hasattr(subject, "favorite")

    # Test invalid ID
    subject_none = repo.find_subject_by_id(-1)
    assert subject_none is None


def test_find_character_by_id():
    # Test valid ID
    character = repo.find_character_by_id(1)
    assert character is not None
    assert character.id == 1
    assert hasattr(character, "name")

    # Test invalid ID
    character_none = repo.find_character_by_id(-1)
    assert character_none is None


def test_find_person_by_id():
    # Test valid ID
    person = repo.find_person_by_id(1)
    assert person is not None
    assert person.id == 1
    assert hasattr(person, "name")
    assert hasattr(person, "type")

    # Test invalid ID
    person_none = repo.find_person_by_id(-1)
    assert person_none is None


def test_find_episodes_by_subject_id():
    # Test valid subject ID
    episodes = repo.find_episodes_by_subject_id(1)
    assert isinstance(episodes, list)
    # May be empty list if subject has no episodes

    # Test invalid subject ID
    episodes_empty = repo.find_episodes_by_subject_id(-1)
    assert isinstance(episodes_empty, list)
    assert len(episodes_empty) == 0


def test_find_subjects_by_ids():
    # Test valid IDs
    subjects = repo.find_subjects_by_ids([1, 2])
    assert isinstance(subjects, list)
    assert len(subjects) > 0
    for subject in subjects:
        assert subject.id in [1, 2]

    # Test invalid IDs
    subjects_none = repo.find_subjects_by_ids([-1, -2])
    assert isinstance(subjects_none, list)
    assert len(subjects_none) == 0

    # Test empty list
    subjects_empty = repo.find_subjects_by_ids([])
    assert isinstance(subjects_empty, list)
    assert len(subjects_empty) == 0


def test_find_characters_by_ids():
    # Test valid IDs
    characters = repo.find_characters_by_ids([1, 2])
    assert isinstance(characters, list)
    # May be empty if characters don't exist

    # Test invalid IDs
    characters_none = repo.find_characters_by_ids([-1, -2])
    assert isinstance(characters_none, list)
    assert len(characters_none) == 0

    # Test empty list
    characters_empty = repo.find_characters_by_ids([])
    assert isinstance(characters_empty, list)
    assert len(characters_empty) == 0


def test_find_people_by_ids():
    # Test valid IDs
    people = repo.find_people_by_ids([1, 2])
    assert isinstance(people, list)
    # May be empty if people don't exist

    # Test invalid IDs
    people_none = repo.find_people_by_ids([-1, -2])
    assert isinstance(people_none, list)
    assert len(people_none) == 0

    # Test empty list
    people_empty = repo.find_people_by_ids([])
    assert isinstance(people_empty, list)
    assert len(people_empty) == 0

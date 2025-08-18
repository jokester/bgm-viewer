import pytest
from unittest.mock import AsyncMock
from .subject_index import SubjectsIndex, SubjectsIndexQuery
from .character_index import CharacterIndex, CharactersIndexQuery
from .person_index import PersonIndex, PersonsIndexQuery
from .episode_index import EpisodeIndex, EpisodesIndexQuery


@pytest.fixture
def mock_es_client():
    """Mock Elasticsearch client for testing."""
    client = AsyncMock()
    return client


@pytest.fixture
def subjects_index(mock_es_client) -> SubjectsIndex:
    """SubjectsIndex instance with mocked ES client."""
    return SubjectsIndex(mock_es_client, "test_subjects")


@pytest.fixture
def characters_index(mock_es_client) -> CharacterIndex:
    """CharacterIndex instance with mocked ES client."""
    return CharacterIndex(mock_es_client, "test_characters")


@pytest.fixture
def persons_index(mock_es_client) -> PersonIndex:
    """PersonIndex instance with mocked ES client."""
    return PersonIndex(mock_es_client, "test_persons")


@pytest.fixture
def episodes_index(mock_es_client) -> EpisodeIndex:
    """EpisodeIndex instance with mocked ES client."""
    return EpisodeIndex(mock_es_client, "test_episodes")


# Common test for empty results
@pytest.mark.asyncio
async def test_search_empty_results_all_indexes(
    characters_index, persons_index, episodes_index, mock_es_client
):
    """Test search with no results for all indexes."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    # Test all indexes
    char_results = await characters_index.search(
        CharactersIndexQuery(query="nonexistent")
    )
    person_results = await persons_index.search(PersonsIndexQuery(query="nonexistent"))
    episode_results = await episodes_index.search(
        EpisodesIndexQuery(query="nonexistent")
    )

    assert char_results.total == 0
    assert person_results.total == 0
    assert episode_results.total == 0

    assert len(char_results.items) == 0
    assert len(person_results.items) == 0
    assert len(episode_results.items) == 0


# Common test for invalid data handling
@pytest.mark.asyncio
async def test_search_invalid_data_handling_all_indexes(
    characters_index, persons_index, episodes_index, mock_es_client
):
    """Test search handles invalid data gracefully for all indexes."""
    # Mock response with one valid and one invalid hit for each index type
    mock_response_characters = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "Valid Character",
                        "infobox": "Valid infobox",
                        "summary": "Valid summary",
                        "comments": 0,
                        "collects": 0,
                    }
                },
                {
                    "_source": {
                        "id": 2,
                        "invalid_field": "invalid_data",  # Missing required fields
                    }
                },
            ],
            "total": {"value": 2},
        }
    }

    mock_response_persons = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "Valid Person",
                        "type": 1,  # INDIVIDUAL
                        "career": ["Director"],
                        "infobox": "Valid infobox",
                        "summary": "Valid summary",
                        "comments": 0,
                        "collects": 0,
                    }
                },
                {
                    "_source": {
                        "id": 2,
                        "invalid_field": "invalid_data",  # Missing required fields
                    }
                },
            ],
            "total": {"value": 2},
        }
    }

    mock_response_episodes = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "Valid Episode",
                        "name_cn": "有效集数",
                        "description": "Valid description",
                        "airdate": "2023-01-01",
                        "disc": 1,
                        "duration": "24:00",
                        "subject_id": 100,
                        "sort": 1.0,
                        "type": 0,  # MAIN
                    }
                },
                {
                    "_source": {
                        "id": 2,
                        "invalid_field": "invalid_data",  # Missing required fields
                    }
                },
            ],
            "total": {"value": 2},
        }
    }

    # Test each index separately with appropriate mock data
    mock_es_client.search.return_value = mock_response_characters
    char_results = await characters_index.search(CharactersIndexQuery(query="test"))

    mock_es_client.search.return_value = mock_response_persons
    person_results = await persons_index.search(PersonsIndexQuery(query="test"))

    mock_es_client.search.return_value = mock_response_episodes
    episode_results = await episodes_index.search(EpisodesIndexQuery(query="test"))

    # Each should return only the valid result
    assert char_results.total == 2
    assert person_results.total == 2
    assert episode_results.total == 2

    assert len(char_results.items) == 1
    assert len(person_results.items) == 1
    assert len(episode_results.items) == 1

    assert char_results.items[0].id == 1
    assert person_results.items[0].id == 1
    assert episode_results.items[0].id == 1

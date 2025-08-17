import pytest
from unittest.mock import AsyncMock, MagicMock
from .subject_index import SubjectsIndex, SubjectsIndexQuery
from bgm_archive.loader import model


@pytest.fixture
def mock_es_client():
    """Mock Elasticsearch client for testing."""
    client = AsyncMock()
    return client


@pytest.fixture
def subjects_index(mock_es_client) -> SubjectsIndex:
    """SubjectsIndex instance with mocked ES client."""
    return SubjectsIndex(mock_es_client, "test_subjects")


@pytest.mark.asyncio
async def test_search_subjects_basic(subjects_index, mock_es_client):
    """Test basic search functionality."""
    # Mock search response
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "type": 2,  # ANIME
                        "name": "Test Anime",
                        "name_cn": "测试动画",
                        "infobox": "Test infobox",
                        "platform": 1,
                        "summary": "Test summary",
                        "nsfw": False,
                        "tags": [{"name": "test", "count": 1}],
                        "score": 8.5,
                        "rank": 100,
                        "date": "2023-01-01",
                        "favorite": {
                            "wish": 10,
                            "done": 100,
                            "doing": 20,
                            "on_hold": 5,
                            "dropped": 2,
                        },
                        "series": False,
                        "meta_tags": ["test"],
                    }
                }
            ]
        }
    }

    mock_es_client.search.return_value = mock_response

    # Create search query
    search_query = SubjectsIndexQuery(query="test anime")

    # Perform search
    results = await subjects_index.search(search_query)

    # Verify results
    assert len(results) == 1
    assert results[0].id == 1
    assert results[0].name == "Test Anime"
    assert results[0].type == model.SubjectType.ANIME

    # Verify ES client was called correctly
    mock_es_client.search.assert_called_once()
    call_args = mock_es_client.search.call_args
    assert call_args[1]["index"] == "test_subjects"

    # Verify query structure
    query_body = call_args[1]["body"]
    assert (
        query_body["query"]["bool"]["must"][0]["multi_match"]["query"] == "test anime"
    )
    assert query_body["size"] == 20  # default limit
    assert query_body["from"] == 0  # default offset


@pytest.mark.asyncio
async def test_search_subjects_with_filters(subjects_index, mock_es_client):
    """Test search with filters."""
    mock_response = {"hits": {"hits": []}}
    mock_es_client.search.return_value = mock_response

    # Create search query with filters
    search_query = SubjectsIndexQuery(
        query="test",
        limit=10,
        offset=5,
        subject_type=2,  # ANIME
        nsfw=False,
    )

    # Perform search
    await subjects_index.search(search_query)

    # Verify filters were applied
    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Check filters
    filters = query_body["query"]["bool"]["filter"]
    assert len(filters) == 2

    # Subject type filter
    type_filter = next(f for f in filters if "term" in f and "type" in f["term"])
    assert type_filter["term"]["type"] == 2

    # NSFW filter
    nsfw_filter = next(f for f in filters if "term" in f and "nsfw" in f["term"])
    assert nsfw_filter["term"]["nsfw"] is False

    # Check pagination
    assert query_body["size"] == 10
    assert query_body["from"] == 5


@pytest.mark.asyncio
async def test_search_subjects_empty_results(subjects_index, mock_es_client):
    """Test search with no results."""
    mock_response = {"hits": {"hits": []}}
    mock_es_client.search.return_value = mock_response

    search_query = SubjectsIndexQuery(query="nonexistent")
    results = await subjects_index.search(search_query)

    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_subjects_invalid_data_handling(subjects_index, mock_es_client):
    """Test search handles invalid data gracefully."""
    # Mock response with one valid and one invalid hit
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "type": 2,
                        "name": "Valid Anime",
                        "name_cn": "有效动画",
                        "infobox": "Valid infobox",
                        "platform": 1,
                        "summary": "Valid summary",
                        "nsfw": False,
                        "tags": [],
                        "score": 8.0,
                        "rank": 100,
                        "date": "2023-01-01",
                        "favorite": {
                            "wish": 0,
                            "done": 0,
                            "doing": 0,
                            "on_hold": 0,
                            "dropped": 0,
                        },
                        "series": False,
                        "meta_tags": [],
                    }
                },
                {
                    "_source": {
                        "id": 2,
                        "invalid_field": "invalid_data",  # Missing required fields
                    }
                },
            ]
        }
    }

    mock_es_client.search.return_value = mock_response

    search_query = SubjectsIndexQuery(query="test")
    results = await subjects_index.search(search_query)

    # Should return only the valid result
    assert len(results) == 1
    assert results[0].id == 1
    assert results[0].name == "Valid Anime"

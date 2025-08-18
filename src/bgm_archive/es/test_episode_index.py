import pytest
from bgm_archive.loader import model
from .test_common import mock_es_client, episodes_index
from .episode_index import EpisodesIndexQuery


@pytest.mark.asyncio
async def test_search_episodes_basic(episodes_index, mock_es_client):
    """Test basic search functionality."""
    # Mock search response
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "Test Episode",
                        "name_cn": "测试集数",
                        "description": "Test description",
                        "airdate": "2023-01-01",
                        "disc": 1,
                        "duration": "24:00",
                        "subject_id": 100,
                        "sort": 1.0,
                        "type": 0,  # MAIN
                    }
                }
            ],
            "total": {"value": 1},
        }
    }

    mock_es_client.search.return_value = mock_response

    # Create search query
    search_query = EpisodesIndexQuery(query="test episode")

    # Perform search
    results = await episodes_index.search(search_query)

    # Verify results
    assert results.total == 1
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Test Episode"
    assert results.items[0].type == model.EpisodeType.MAIN

    # Verify ES client was called correctly
    mock_es_client.search.assert_called_once()
    call_args = mock_es_client.search.call_args
    assert call_args[1]["index"] == "test_episodes"

    # Verify query structure
    query_body = call_args[1]["body"]
    assert (
        query_body["query"]["bool"]["must"][0]["multi_match"]["query"] == "test episode"
    )
    assert query_body["size"] == 20  # default limit
    assert query_body["from"] == 0  # default offset


@pytest.mark.asyncio
async def test_search_episodes_with_filters(episodes_index, mock_es_client):
    """Test search with filters."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    # Create search query with filters
    search_query = EpisodesIndexQuery(
        query="test",
        limit=10,
        offset=5,
        type=0,  # MAIN
        subject_id=100,
    )

    # Perform search
    await episodes_index.search(search_query)

    # Verify filters were applied
    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Check filters
    filters = query_body["query"]["bool"]["filter"]
    assert len(filters) == 2

    # Type filter
    type_filter = next(f for f in filters if "term" in f and "type" in f["term"])
    assert type_filter["term"]["type"] == 0

    # Subject ID filter
    subject_filter = next(
        f for f in filters if "term" in f and "subject_id" in f["term"]
    )
    assert subject_filter["term"]["subject_id"] == 100

    # Verify pagination
    assert query_body["size"] == 10
    assert query_body["from"] == 5


@pytest.mark.asyncio
async def test_search_episodes_pagination(episodes_index, mock_es_client):
    """Test search pagination."""
    # Mock response with multiple results
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": i,
                        "name": f"Episode {i}",
                        "name_cn": f"集数{i}",
                        "description": f"Description {i}",
                        "airdate": "2023-01-01",
                        "disc": 1,
                        "duration": "24:00",
                        "subject_id": 100,
                        "sort": float(i),
                        "type": 0,
                    }
                }
                for i in range(1, 6)  # 5 results
            ],
            "total": {"value": 25},  # Total of 25 results
        }
    }

    mock_es_client.search.return_value = mock_response

    # Test first page
    search_query = EpisodesIndexQuery(query="episode", limit=5, offset=0)
    results = await episodes_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 0
    assert results.has_more is True  # Should have more results

    # Test second page
    search_query = EpisodesIndexQuery(query="episode", limit=5, offset=5)
    results = await episodes_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 5
    assert results.has_more is True  # Should have more results

    # Test last page
    search_query = EpisodesIndexQuery(query="episode", limit=5, offset=20)
    results = await episodes_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 20
    assert results.has_more is False  # Should not have more results


@pytest.mark.asyncio
async def test_search_episodes_sorting(episodes_index, mock_es_client):
    """Test search result sorting."""
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "First Episode",
                        "name_cn": "第一集",
                        "description": "Description",
                        "airdate": "2023-01-01",
                        "disc": 1,
                        "duration": "24:00",
                        "subject_id": 100,
                        "sort": 1.0,
                        "type": 0,
                    }
                }
            ],
            "total": {"value": 1},
        }
    }

    mock_es_client.search.return_value = mock_response

    search_query = EpisodesIndexQuery(query="episode")
    await episodes_index.search(search_query)

    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Verify sorting
    sort = query_body["sort"]
    assert len(sort) == 2
    assert sort[0] == {"_score": {"order": "desc"}}
    assert sort[1] == {"sort": {"order": "asc"}}


@pytest.mark.asyncio
async def test_search_episodes_query_structure(episodes_index, mock_es_client):
    """Test search query structure."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = EpisodesIndexQuery(query="test query")
    await episodes_index.search(search_query)

    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Verify multi-match query structure
    multi_match = query_body["query"]["bool"]["must"][0]["multi_match"]
    assert multi_match["query"] == "test query"
    assert multi_match["type"] == "best_fields"
    assert multi_match["fuzziness"] == "AUTO"

    # Verify search fields
    expected_fields = [
        "name^3",
        "name_cn^3",
        "description^2",
    ]
    assert multi_match["fields"] == expected_fields


@pytest.mark.asyncio
async def test_search_episodes_empty_query(episodes_index, mock_es_client):
    """Test search with empty query."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = EpisodesIndexQuery(query="")
    results = await episodes_index.search(search_query)

    assert results.total == 0
    assert len(results.items) == 0
    assert results.query == ""
    assert results.limit == 20  # default
    assert results.offset == 0  # default
    assert results.has_more is False


@pytest.mark.asyncio
async def test_search_episodes_invalid_data_handling(episodes_index, mock_es_client):
    """Test search handles invalid data gracefully."""
    # Mock response with one valid and one invalid hit
    mock_response = {
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
                        "type": 0,
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

    mock_es_client.search.return_value = mock_response

    search_query = EpisodesIndexQuery(query="test")
    results = await episodes_index.search(search_query)

    # Should return only the valid result
    assert results.total == 2
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Valid Episode"

import pytest
from bgm_archive.loader import model
from .test_common import mock_es_client, subjects_index
from .subject_index import SubjectsIndexQuery


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
            ],
            "total": {"value": 1},
        }
    }

    mock_es_client.search.return_value = mock_response

    # Create search query
    search_query = SubjectsIndexQuery(query="test anime")

    # Perform search
    results = await subjects_index.search(search_query)

    # Verify results
    assert results.total == 1
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Test Anime"
    assert results.items[0].type == model.SubjectType.ANIME

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
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
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

    # Verify pagination
    assert query_body["size"] == 10
    assert query_body["from"] == 5


@pytest.mark.asyncio
async def test_search_subjects_pagination(subjects_index, mock_es_client):
    """Test search pagination."""
    # Mock response with multiple results
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": i,
                        "type": 2,
                        "name": f"Anime {i}",
                        "name_cn": f"动画{i}",
                        "infobox": f"Infobox {i}",
                        "platform": 1,
                        "summary": f"Summary {i}",
                        "nsfw": False,
                        "tags": [],
                        "score": 8.0,
                        "rank": 100 + i,
                        "date": "2023-01-01",
                        "favorite": {
                            "wish": 10,
                            "done": 100,
                            "doing": 20,
                            "on_hold": 5,
                            "dropped": 2,
                        },
                        "series": False,
                        "meta_tags": [],
                    }
                }
                for i in range(1, 6)  # 5 results
            ],
            "total": {"value": 25},  # Total of 25 results
        }
    }

    mock_es_client.search.return_value = mock_response

    # Test first page
    search_query = SubjectsIndexQuery(query="anime", limit=5, offset=0)
    results = await subjects_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 0
    assert results.has_more is True  # Should have more results

    # Test second page
    search_query = SubjectsIndexQuery(query="anime", limit=5, offset=5)
    results = await subjects_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 5
    assert results.has_more is True  # Should have more results

    # Test last page
    search_query = SubjectsIndexQuery(query="anime", limit=5, offset=20)
    results = await subjects_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 20
    assert results.has_more is False  # Should not have more results


@pytest.mark.asyncio
async def test_search_subjects_sorting(subjects_index, mock_es_client):
    """Test search result sorting."""
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "type": 2,
                        "name": "High Score Anime",
                        "name_cn": "高分动画",
                        "infobox": "Infobox",
                        "platform": 1,
                        "summary": "Summary",
                        "nsfw": False,
                        "tags": [],
                        "score": 9.5,
                        "rank": 50,
                        "date": "2023-01-01",
                        "favorite": {
                            "wish": 10,
                            "done": 100,
                            "doing": 20,
                            "on_hold": 5,
                            "dropped": 2,
                        },
                        "series": False,
                        "meta_tags": [],
                    }
                }
            ],
            "total": {"value": 1},
        }
    }

    mock_es_client.search.return_value = mock_response

    search_query = SubjectsIndexQuery(query="anime")
    await subjects_index.search(search_query)

    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Verify sorting
    sort = query_body["sort"]
    assert len(sort) == 3
    assert sort[0] == {"_score": {"order": "desc"}}
    assert sort[1] == {"score": {"order": "desc"}}
    assert sort[2] == {"rank": {"order": "asc"}}


@pytest.mark.asyncio
async def test_search_subjects_query_structure(subjects_index, mock_es_client):
    """Test search query structure."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = SubjectsIndexQuery(query="test query")
    await subjects_index.search(search_query)

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
        "summary^2",
        "infobox^1",
        "tags.name^2",
    ]
    assert multi_match["fields"] == expected_fields


@pytest.mark.asyncio
async def test_search_subjects_empty_query(subjects_index, mock_es_client):
    """Test search with empty query."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = SubjectsIndexQuery(query="")
    results = await subjects_index.search(search_query)

    assert results.total == 0
    assert len(results.items) == 0
    assert results.query == ""
    assert results.limit == 20  # default
    assert results.offset == 0  # default
    assert results.has_more is False


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
                            "wish": 10,
                            "done": 100,
                            "doing": 20,
                            "on_hold": 5,
                            "dropped": 2,
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
            ],
            "total": {"value": 2},
        }
    }

    mock_es_client.search.return_value = mock_response

    search_query = SubjectsIndexQuery(query="test")
    results = await subjects_index.search(search_query)

    # Should return only the valid result
    assert results.total == 2
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Valid Anime"

import pytest
from bgm_archive.loader import model
from .test_common import mock_es_client, persons_index
from .person_index import PersonsIndexQuery


@pytest.mark.asyncio
async def test_search_persons_basic(persons_index, mock_es_client):
    """Test basic search functionality."""
    # Mock search response
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "Test Person",
                        "type": 1,  # INDIVIDUAL
                        "career": ["Director"],
                        "infobox": "Test infobox",
                        "summary": "Test summary",
                        "comments": 10,
                        "collects": 100,
                    }
                }
            ],
            "total": {"value": 1},
        }
    }

    mock_es_client.search.return_value = mock_response

    # Create search query
    search_query = PersonsIndexQuery(query="test person")

    # Perform search
    results = await persons_index.search(search_query)

    # Verify results
    assert results.total == 1
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Test Person"
    assert results.items[0].type == model.PersonType.INDIVIDUAL

    # Verify ES client was called correctly
    mock_es_client.search.assert_called_once()
    call_args = mock_es_client.search.call_args
    assert call_args[1]["index"] == "test_persons"

    # Verify query structure
    query_body = call_args[1]["body"]
    assert (
        query_body["query"]["bool"]["must"][0]["multi_match"]["query"] == "test person"
    )
    assert query_body["size"] == 20  # default limit
    assert query_body["from"] == 0  # default offset


@pytest.mark.asyncio
async def test_search_persons_with_filters(persons_index, mock_es_client):
    """Test search with filters."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    # Create search query with filters
    search_query = PersonsIndexQuery(
        query="test",
        limit=10,
        offset=5,
        type=1,  # INDIVIDUAL
        career="Director",
    )

    # Perform search
    await persons_index.search(search_query)

    # Verify filters were applied
    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Check filters
    filters = query_body["query"]["bool"]["filter"]
    assert len(filters) == 2

    # Type filter
    type_filter = next(f for f in filters if "term" in f and "type" in f["term"])
    assert type_filter["term"]["type"] == 1

    # Career filter
    career_filter = next(f for f in filters if "term" in f and "career" in f["term"])
    assert career_filter["term"]["career"] == "Director"

    # Verify pagination
    assert query_body["size"] == 10
    assert query_body["from"] == 5


@pytest.mark.asyncio
async def test_search_persons_pagination(persons_index, mock_es_client):
    """Test search pagination."""
    # Mock response with multiple results
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": i,
                        "name": f"Person {i}",
                        "type": 1,
                        "career": [f"Career {i}"],
                        "infobox": f"Infobox {i}",
                        "summary": f"Summary {i}",
                        "comments": 10 + i,
                        "collects": 100 + i,
                    }
                }
                for i in range(1, 6)  # 5 results
            ],
            "total": {"value": 25},  # Total of 25 results
        }
    }

    mock_es_client.search.return_value = mock_response

    # Test first page
    search_query = PersonsIndexQuery(query="person", limit=5, offset=0)
    results = await persons_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 0
    assert results.has_more is True  # Should have more results

    # Test second page
    search_query = PersonsIndexQuery(query="person", limit=5, offset=5)
    results = await persons_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 5
    assert results.has_more is True  # Should have more results

    # Test last page
    search_query = PersonsIndexQuery(query="person", limit=5, offset=20)
    results = await persons_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 20
    assert results.has_more is False  # Should not have more results


@pytest.mark.asyncio
async def test_search_persons_sorting(persons_index, mock_es_client):
    """Test search result sorting."""
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "Popular Person",
                        "type": 1,
                        "career": ["Director"],
                        "infobox": "Infobox",
                        "summary": "Summary",
                        "comments": 100,
                        "collects": 1000,
                    }
                }
            ],
            "total": {"value": 1},
        }
    }

    mock_es_client.search.return_value = mock_response

    search_query = PersonsIndexQuery(query="person")
    await persons_index.search(search_query)

    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Verify sorting
    sort = query_body["sort"]
    assert len(sort) == 3
    assert sort[0] == {"_score": {"order": "desc"}}
    assert sort[1] == {"collects": {"order": "desc"}}
    assert sort[2] == {"comments": {"order": "desc"}}


@pytest.mark.asyncio
async def test_search_persons_query_structure(persons_index, mock_es_client):
    """Test search query structure."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = PersonsIndexQuery(query="test query")
    await persons_index.search(search_query)

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
        "summary^2",
        "infobox^1",
        "career^2",
    ]
    assert multi_match["fields"] == expected_fields


@pytest.mark.asyncio
async def test_search_persons_empty_query(persons_index, mock_es_client):
    """Test search with empty query."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = PersonsIndexQuery(query="")
    results = await persons_index.search(search_query)

    assert results.total == 0
    assert len(results.items) == 0
    assert results.query == ""
    assert results.limit == 20  # default
    assert results.offset == 0  # default
    assert results.has_more is False


@pytest.mark.asyncio
async def test_search_persons_invalid_data_handling(persons_index, mock_es_client):
    """Test search handles invalid data gracefully."""
    # Mock response with one valid and one invalid hit
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "name": "Valid Person",
                        "type": 1,
                        "career": ["Director"],
                        "infobox": "Valid infobox",
                        "summary": "Valid summary",
                        "comments": 10,
                        "collects": 100,
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

    search_query = PersonsIndexQuery(query="test")
    results = await persons_index.search(search_query)

    # Should return only the valid result
    assert results.total == 2
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Valid Person"

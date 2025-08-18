import pytest
from bgm_archive.loader import model
from .test_common import mock_es_client, characters_index
from .character_index import CharactersIndexQuery


@pytest.mark.asyncio
async def test_search_characters_basic(characters_index, mock_es_client):
    """Test basic search functionality."""
    # Mock search response
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "role": 1,  # MAIN
                        "name": "Test Character",
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
    search_query = CharactersIndexQuery(query="test character")

    # Perform search
    results = await characters_index.search(search_query)

    # Verify results
    assert results.total == 1
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Test Character"
    assert results.items[0].role == model.CharacterRole.MAIN

    # Verify ES client was called correctly
    mock_es_client.search.assert_called_once()
    call_args = mock_es_client.search.call_args
    assert call_args[1]["index"] == "test_characters"

    # Verify query structure
    query_body = call_args[1]["body"]
    assert (
        query_body["query"]["bool"]["must"][0]["multi_match"]["query"]
        == "test character"
    )
    assert query_body["size"] == 20  # default limit
    assert query_body["from"] == 0  # default offset


@pytest.mark.asyncio
async def test_search_characters_with_filters(characters_index, mock_es_client):
    """Test search with filters."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    # Create search query with filters
    search_query = CharactersIndexQuery(
        query="test",
        limit=10,
        offset=5,
        role=1,  # MAIN
    )

    # Perform search
    await characters_index.search(search_query)

    # Verify filters were applied
    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Check filters
    filters = query_body["query"]["bool"]["filter"]
    assert len(filters) == 1

    # Role filter
    role_filter = next(f for f in filters if "term" in f and "role" in f["term"])
    assert role_filter["term"]["role"] == 1

    # Verify pagination
    assert query_body["size"] == 10
    assert query_body["from"] == 5


@pytest.mark.asyncio
async def test_search_characters_pagination(characters_index, mock_es_client):
    """Test search pagination."""
    # Mock response with multiple results
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": i,
                        "role": 1,
                        "name": f"Character {i}",
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
    search_query = CharactersIndexQuery(query="character", limit=5, offset=0)
    results = await characters_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 0
    assert results.has_more is True  # Should have more results

    # Test second page
    search_query = CharactersIndexQuery(query="character", limit=5, offset=5)
    results = await characters_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 5
    assert results.has_more is True  # Should have more results

    # Test last page
    search_query = CharactersIndexQuery(query="character", limit=5, offset=20)
    results = await characters_index.search(search_query)

    assert results.total == 25
    assert len(results.items) == 5
    assert results.limit == 5
    assert results.offset == 20
    assert results.has_more is False  # Should not have more results


@pytest.mark.asyncio
async def test_search_characters_sorting(characters_index, mock_es_client):
    """Test search result sorting."""
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "role": 1,
                        "name": "Popular Character",
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

    search_query = CharactersIndexQuery(query="character")
    await characters_index.search(search_query)

    call_args = mock_es_client.search.call_args
    query_body = call_args[1]["body"]

    # Verify sorting
    sort = query_body["sort"]
    assert len(sort) == 3
    assert sort[0] == {"_score": {"order": "desc"}}
    assert sort[1] == {"collects": {"order": "desc"}}
    assert sort[2] == {"comments": {"order": "desc"}}


@pytest.mark.asyncio
async def test_search_characters_query_structure(characters_index, mock_es_client):
    """Test search query structure."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = CharactersIndexQuery(query="test query")
    await characters_index.search(search_query)

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
    ]
    assert multi_match["fields"] == expected_fields


@pytest.mark.asyncio
async def test_search_characters_empty_query(characters_index, mock_es_client):
    """Test search with empty query."""
    mock_response = {"hits": {"hits": [], "total": {"value": 0}}}
    mock_es_client.search.return_value = mock_response

    search_query = CharactersIndexQuery(query="")
    results = await characters_index.search(search_query)

    assert results.total == 0
    assert len(results.items) == 0
    assert results.query == ""
    assert results.limit == 20  # default
    assert results.offset == 0  # default
    assert results.has_more is False


@pytest.mark.asyncio
async def test_search_characters_invalid_data_handling(
    characters_index, mock_es_client
):
    """Test search handles invalid data gracefully."""
    # Mock response with one valid and one invalid hit
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "role": 1,
                        "name": "Valid Character",
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

    search_query = CharactersIndexQuery(query="test")
    results = await characters_index.search(search_query)

    # Should return only the valid result
    assert results.total == 2
    assert len(results.items) == 1
    assert results.items[0].id == 1
    assert results.items[0].name == "Valid Character"

from pydantic import BaseModel
from typing import Optional, List
import logging
from .base_index import BaseIndex, SearchResult
from bgm_archive.loader import model

logger = logging.getLogger(__name__)


class PersonsIndexQuery(BaseModel):
    query: str
    limit: int = 20
    offset: int = 0
    type: Optional[int] = None
    career: Optional[str] = None


class PersonSearchResult(SearchResult[model.Person]):
    """Result model for person search operations."""
    pass


class PersonIndex(BaseIndex[model.Person]):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Person)

    async def search(self, search_query: PersonsIndexQuery) -> PersonSearchResult:
        """Search persons using Elasticsearch."""
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": search_query.query,
                                "fields": [
                                    "name^3",
                                    "summary^2",
                                    "infobox^1",
                                    "career^2",
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                            }
                        }
                    ],
                    "filter": [],
                }
            },
            "size": search_query.limit,
            "from": search_query.offset,
            "sort": [
                {"_score": {"order": "desc"}},
                {"collects": {"order": "desc"}},
                {"comments": {"order": "desc"}},
            ],
        }

        # Add filters if specified
        if search_query.type is not None:
            query_body["query"]["bool"]["filter"].append(
                {"term": {"type": search_query.type}}
            )

        if search_query.career is not None:
            query_body["query"]["bool"]["filter"].append(
                {"term": {"career": search_query.career}}
            )

        response = await self._es.search(index=self._index_name, body=query_body)

        hits = response.get("hits", {}).get("hits", [])
        total = response.get("hits", {}).get("total", {}).get("value", 0)
        
        persons = []
        for hit in hits:
            try:
                person = self._model_type.model_validate(hit["_source"])
                persons.append(person)
            except Exception as e:
                logger.warning(f"Failed to parse person from search result: {e}")
                continue

        has_more = (search_query.offset + search_query.limit) < total
        
        return PersonSearchResult(
            items=persons,
            total=total,
            query=search_query.query,
            limit=search_query.limit,
            offset=search_query.offset,
            has_more=has_more
        )

    @property
    def es_mappings(self) -> dict:
        return {
            "properties": {
                "id": {"type": "long"},
                "name": {"type": "text", "analyzer": "mixed_cjk_english"},
                "type": {"type": "integer"},
                "career": {"type": "keyword"},
                "infobox": {"type": "text", "analyzer": "mixed_cjk_english"},
                "summary": {"type": "text", "analyzer": "mixed_cjk_english"},
                "comments": {"type": "integer"},
                "collects": {"type": "integer"},
            }
        }

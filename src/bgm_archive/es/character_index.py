from pydantic import BaseModel
from typing import Optional, List
import logging
from .base_index import BaseIndex, SearchResult
from bgm_archive.loader import model

logger = logging.getLogger(__name__)


class CharactersIndexQuery(BaseModel):
    query: str
    limit: int = 20
    offset: int = 0


class CharacterSearchResult(SearchResult[model.Character]):
    """Result model for character search operations."""

    pass


class CharacterIndex(BaseIndex[model.Character]):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Character)

    async def search(self, search_query: CharactersIndexQuery) -> CharacterSearchResult:
        """Search characters using Elasticsearch."""
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

        response = await self._es.search(index=self._index_name, body=query_body)

        hits = response.get("hits", {}).get("hits", [])
        total = response.get("hits", {}).get("total", {}).get("value", 0)

        characters = []
        for hit in hits:
            try:
                character = self._model_type.model_validate(hit["_source"])
                characters.append(character)
            except Exception as e:
                logger.warning(f"Failed to parse character from search result: {e}")
                continue

        has_more = (search_query.offset + search_query.limit) < total

        return CharacterSearchResult(
            items=characters,
            total=total,
            query=search_query.query,
            limit=search_query.limit,
            offset=search_query.offset,
            has_more=has_more,
        )

    @property
    def es_mappings(self) -> dict:
        return {
            "properties": {
                "id": {"type": "long"},
                "name": {"type": "text", "analyzer": "mixed_cjk_english"},
                "infobox": {"type": "text", "analyzer": "mixed_cjk_english"},
                "summary": {"type": "text", "analyzer": "mixed_cjk_english"},
                "comments": {"type": "integer"},
                "collects": {"type": "integer"},
            }
        }
